from transpire.resources import Deployment, Ingress, Secret, Service
from transpire.types import Image
from transpire.utils import get_image_tag

name = "strapi"
db_host = f"ocf-{name}"


def images():
    yield Image(name="strapi-production", path=Path("/"), target="strapi-production")

def objects():
    # Postgres database for strapi
    yield {
        "apiVersion": "acid.zalan.do/v1",
        "kind": "postgresql",
        "metadata": {"name": db_host},
        "spec": {
            "teamId": "ocf",
            "volume": {
                "size": "32Gi",
                "storageClass": "rbd-nvme",
            },
            "numberOfInstances": 1,
            "users": {"notes": ["superuser", "createdb"]},
            "databases": {"strapi": "strapi"},
            "postgresql": {"version": "15"},
        }
    }

    secret = Secret(
        "strapi",
        string_data={
            "jwt-secret": "",
            "admin-jwt-secret": "",
            "app-keys": "",
        },
    )
    yield secret.build()
    
    dep = Deployment.simple(name=name, image=get_image_tag("strapi-production"), ports=[1337])

    # https://docs.strapi.io/dev-docs/installation/docker
    env = {
        "DATABASE_CLIENT": "postgres",
        "DATABASE_HOST": db_host,
        "DATABASE_PORT": "5432",
        "DATABASE_NAME": "strapi",
        "NODE_ENV": "production",
    }

    yield dep.build()

    dep.obj.spec.template.spec.containers[0].env = [
        {
            "name": "DATABASE_USERNAME",
            "valueFrom": {
                "secretKeyRef": {
                    "name": "strapi.ocf-strapi.credentials.postgresql.acid.zalan.do",
                    "key": "username",
                }
            },
        },
        {
            "name": "DATABASE_PASSWORD",
            "valueFrom": {
                "secretKeyRef": {
                    "name": "strapi.ocf-strapi.credentials.postgresql.acid.zalan.do",
                    "key": "password",
                }
            },
        },
            {
            "name": "JWT_SECRET",
            "valueFrom": {
                "secretKeyRef": {
                    "name": secret.obj.metadata.name,
                    "key": "jwt-secret",
                }
            },
        },
        {
            "name": "ADMIN_JWT_SECRET",
            "valueFrom": {
                "secretKeyRef": {
                    "name": secret.obj.metadata.name,
                    "key": "admin-jwt-secret",
                }
            },
        },
        {
            "name": "APP_KEYS",
            "valueFrom": {
                "secretKeyRef": {
                    "name": secret.obj.metadata.name,
                    "key": "app-keys",
                }
            },
        },
        *[{"name": k, "value": v} for k, v in env.items()],
    ]

    yield dep.build()

    yield Service(
        name=f"{name}-web",
        selector={Deployment.SELECTOR_LABEL: name},
        port_on_pod=1337,
        port_on_svc=80,
    ).build()

    ing = Ingress.from_svc(
        svc=svc,
        host="strapi.ocf.berkeley.edu",
        path_prefix="/",
    )

    yield ing.build()    

