import rustici_software_cloud_v2 as scorm_cloud

# ScormCloud API credentials
APP_ID = "ZSBCOYAWTG"
SECRET_KEY = "sR0YOQOBhIsk155gftenvkzLAOdnq4tokbASNZtt"

def get_all_registrations():
    # Configure HTTP basic authorization
    config = scorm_cloud.Configuration()
    config.username = APP_ID
    config.password = SECRET_KEY
    scorm_cloud.Configuration().set_default(config)

    # Initialize RegistrationApi
    registration_api = scorm_cloud.RegistrationApi()

    try:
        # Get registrations
        response = registration_api.get_registrations()

        # Print the raw response
        print("Raw API Response:")
        print(response)

        # This call is paginated, so we'll handle that and print each page
        page_number = 1
        while response.more is not None:
            print(f"\nFetching page {page_number + 1}:")
            response = registration_api.get_registrations(more=response.more)
            print(response)
            page_number += 1

    except scorm_cloud.rest.ApiException as e:
        print(f"API Exception: {str(e)}")

if __name__ == "__main__":
    get_all_registrations()