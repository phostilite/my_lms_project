import rustici_software_cloud_v2 as scorm_cloud

# ScormCloud API credentials
APP_ID = "ZSBCOYAWTG"
SECRET_KEY = "sR0YOQOBhIsk155gftenvkzLAOdnq4tokbASNZtt"

def build_launch_link(registration_id):
    # Configure HTTP basic authorization
    config = scorm_cloud.Configuration()
    config.username = APP_ID
    config.password = SECRET_KEY
    scorm_cloud.Configuration().set_default(config)

    # Initialize RegistrationApi
    registration_api = scorm_cloud.RegistrationApi()

    try:
        # Create launch link settings
        settings = scorm_cloud.LaunchLinkRequestSchema(redirect_on_exit_url="Message")

        # Build the launch link
        launch_link = registration_api.build_registration_launch_link(registration_id, settings)

        return launch_link.launch_link

    except scorm_cloud.rest.ApiException as e:
        return f"API Exception: {str(e)}"

if __name__ == "__main__":
    # Let's use the first registration ID from your response
    registration_id = "216938cf-0434-43c1-b06f-d428674c60b3"

    launch_url = build_launch_link(registration_id)
    print(f"Launch URL for registration {registration_id}:")
    print(launch_url)