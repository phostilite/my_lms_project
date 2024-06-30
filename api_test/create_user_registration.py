import rustici_software_cloud_v2 as scorm_cloud
import uuid

# ScormCloud API credentials
APP_ID = "ZSBCOYAWTG"
SECRET_KEY = "sR0YOQOBhIsk155gftenvkzLAOdnq4tokbASNZtt"

def create_registration(course_id, learner_id, learner_first_name, learner_last_name):
    # Configure HTTP basic authorization
    config = scorm_cloud.Configuration()
    config.username = APP_ID
    config.password = SECRET_KEY
    scorm_cloud.Configuration().set_default(config)

    # Initialize RegistrationApi
    registration_api = scorm_cloud.RegistrationApi()

    try:
        # Create a unique registration ID
        registration_id = str(uuid.uuid4())

        # Create learner object
        learner = scorm_cloud.LearnerSchema(
            id=learner_id,
            first_name=learner_first_name,
            last_name=learner_last_name
        )

        # Create registration object
        registration = scorm_cloud.CreateRegistrationSchema(
            course_id=course_id,
            learner=learner,
            registration_id=registration_id
        )

        # Create the registration and return the raw result
        create_result = registration_api.create_registration(registration)
        
        return f"Raw create_registration result: {create_result}"

    except scorm_cloud.rest.ApiException as e:
        return f"API Exception: {str(e)}"

if __name__ == "__main__":
    course_id = "C1"  # Use the course ID from the previous output
    learner_id = "learner_001"  # Using a new learner ID to avoid conflicts
    learner_first_name = "Jane"
    learner_last_name = "Doe"

    result = create_registration(course_id, learner_id, learner_first_name, learner_last_name)
    print(result)