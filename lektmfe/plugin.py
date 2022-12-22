import os
from glob import glob

import pkg_resources
from lekt import hooks as lekt_hooks

from .__about__ import __version__

config = {
    "defaults": {
        "VERSION": __version__,
        "DOCKER_IMAGE": "{{ DOCKER_REGISTRY }}mastergowen/openedx-mfe:{{ MFE_VERSION }}",
        "HOST": "apps.{{ LMS_HOST }}",
        "COMMON_VERSION": "{{ OPENEDX_COMMON_VERSION }}",
        "CADDY_DOCKER_IMAGE": "{{ DOCKER_IMAGE_CADDY }}",
        "ACCOUNT_MFE_APP": {
            "name": "account",
            "repository": "https://github.com/lektorium-tutor/frontend-app-account",
            "port": 1997,
            "env": {
                "production": {
                    "COACHING_ENABLED": "",
                    "ENABLE_DEMOGRAPHICS_COLLECTION": "",
                },
            },
        },
        "GRADEBOOK_MFE_APP": {
            "name": "gradebook",
            "repository": "https://github.com/lektorium-tutor/frontend-app-gradebook",
            "port": 1994,
        },
        "LEARNING_MFE_APP": {
            "name": "learning",
            "repository": "https://github.com/lektorium-tutor/frontend-app-learning",
            "port": 2000,
        },
        "PROFILE_MFE_APP": {
            "name": "profile",
            "repository": "https://github.com/lektorium-tutor/frontend-app-profile",
            "port": 1995,
            "env": {
                "production": {
                    "ENABLE_LEARNER_RECORD_MFE": "true",
                },
            },
        },

        "MFE_AUTHN_MFE_APP": {
            "name": "authn",
            "repository": "https://github.com/lektorium-tutor/frontend-app-authn",
            "port": 1999,
            "env": {
                "production": {
                    "MFE_COMMON_VERSION": "lekt"
                },
                "development": {
                    "MFE_COMMON_VERSION": "lekt"
                },
            },
        },

    },
}

lekt_hooks.Filters.COMMANDS_INIT.add_item(
    (
        "lms",
        ("mfe", "tasks", "lms", "init"),
    )
)
lekt_hooks.Filters.IMAGES_BUILD.add_item(
    (
        "mfe",
        ("plugins", "mfe", "build", "mfe"),
        "{{ MFE_DOCKER_IMAGE }}",
        (),
    )
)
lekt_hooks.Filters.IMAGES_PULL.add_item(
    (
        "mfe",
        "{{ MFE_DOCKER_IMAGE }}",
    )
)
lekt_hooks.Filters.IMAGES_PUSH.add_item(
    (
        "mfe",
        "{{ MFE_DOCKER_IMAGE }}",
    )
)



@lekt_hooks.Filters.COMPOSE_MOUNTS.add()
def _mount_frontend_apps(volumes, name):
    """
    If the user mounts any repo named frontend-app-APPNAME, then make sure
    it's available in the APPNAME service container. This is only applicable
    in dev mode, because in production, all MFEs are built and hosted on the
    singular 'mfe' service container.
    """
    prefix = "frontend-app-"
    if name.startswith(prefix):
        # Assumption:
        # For each repo named frontend-app-APPNAME, there is an associated
        # docker-compose service named APPNAME. If this assumption is broken,
        # then Lekt will try to mount the repo in a service that doesn't exist.
        app_name = name.split(prefix)[1]
        volumes += [(app_name, "/openedx/app")]
    return volumes


@lekt_hooks.Filters.IMAGES_PULL.add()
@lekt_hooks.Filters.IMAGES_PUSH.add()
def _add_remote_mfe_image_iff_customized(images, user_config):
    """
    Register MFE image for pushing & pulling if and only if it has
    been set to something other than the default.

    This is work-around to an upstream issue with MFE config. Briefly:
    User config is baked into MFE builds, so Lekt cannot host a generic
    pre-built MFE image. Howevever, individual Lekt users may want/need to
    build and host their own MFE image. So, as a compromise, we tell Lekt
    to push/pull the MFE image if the user/projects/urfu/tutor-edx/lekt/venv/bin/python3.8 has customized it to anything
    other than the default image URL.
    """
    image_tag = user_config["MFE_DOCKER_IMAGE"]
    if not image_tag.startswith("docker.io/mastergowen/openedx-mfe:"):
        # Image has been customized. Add to list for pulling/pushing.
        images.append(("mfe", image_tag))
    return images


####### Boilerplate code
# Add the "templates" folder as a template root
lekt_hooks.Filters.ENV_TEMPLATE_ROOTS.add_item(
    pkg_resources.resource_filename("lektmfe", "templates")
)
# Render the "build" and "apps" folders
lekt_hooks.Filters.ENV_TEMPLATE_TARGETS.add_items(
    [
        ("mfe/build", "plugins"),
        ("mfe/apps", "plugins"),
    ],
)
# Load patches from files
for path in glob(
        os.path.join(
            pkg_resources.resource_filename("lektmfe", "patches"),
            "*",
        )
):
    with open(path, encoding="utf-8") as patch_file:
        lekt_hooks.Filters.ENV_PATCHES.add_item((os.path.basename(path), patch_file.read()))

# Add configuration entries
lekt_hooks.Filters.CONFIG_DEFAULTS.add_items(
    [(f"MFE_{key}", value) for key, value in config.get("defaults", {}).items()]
)
lekt_hooks.Filters.CONFIG_UNIQUE.add_items(
    [(f"MFE_{key}", value) for key, value in config.get("unique", {}).items()]
)
lekt_hooks.Filters.CONFIG_OVERRIDES.add_items(list(config.get("overrides", {}).items()))
