import rustici_software_cloud_v2 as scorm_cloud
import json

# ScormCloud API credentials
APP_ID = "ZSBCOYAWTG"
SECRET_KEY = "sR0YOQOBhIsk155gftenvkzLAOdnq4tokbASNZtt"

def get_all_courses():
    # Configure HTTP basic authorization
    config = scorm_cloud.Configuration()
    config.username = APP_ID
    config.password = SECRET_KEY
    scorm_cloud.Configuration().set_default(config)

    # Initialize CourseApi
    course_api = scorm_cloud.CourseApi()

    try:
        # Get courses
        response = course_api.get_courses()

        print("Raw API Response:", response)

        # This call is paginated, so we need to handle that
        course_list = response.courses
        while response.more is not None:
            response = course_api.get_courses(more=response.more)
            course_list += response.courses

        # Convert course list to JSON-serializable format
        courses_json = []
        for course in course_list:
            courses_json.append({
                'id': course.id,
                'title': course.title,
                'version': course.version,
                'registration_count': course.registration_count,
                'updated': course.updated.isoformat() if course.updated else None,
                'created': course.created.isoformat() if course.created else None,
            })

        # Return JSON response
        return json.dumps(courses_json, indent=2)

    except scorm_cloud.rest.ApiException as e:
        return json.dumps({"error": str(e)}, indent=2)

if __name__ == "__main__":
    result = get_all_courses()
    print(result)