import streamlit as st

# Dummy data for courses (you can replace it with your actual data)
courses_data = [
    {"name": "Python Programming", "duration": "6 weeks", "certification": True, "owner": "Google"},
    {"name": "Machine Learning Basics", "duration": "8 weeks", "certification": False, "owner": "IBM"},
    {"name": "Web Development Fundamentals", "duration": "4 weeks", "certification": True, "owner": "Openclassroom"},
    # Add more courses as needed
]

def filter_courses(user_input, duration_filter, certification_filter, owner_filter):
    filtered_courses = []
    for course in courses_data:
        if user_input.lower() in course["name"].lower() and \
                (not duration_filter or duration_filter.lower() in course["duration"].lower()) and \
                (not certification_filter or (certification_filter.lower() == "certified" and course["certification"]) or
                 (certification_filter.lower() == "non-certified" and not course["certification"])) and \
                (not owner_filter or owner_filter.lower() == course["owner"].lower()):
            filtered_courses.append(course)
    return filtered_courses

# Streamlit app
def main():
    st.title("Skill Improvement App")

    # User input
    user_input = st.text_input("What do you want to learn?")

    # Filters
    duration_filter = st.text_input("Duration Filter (e.g., 6 weeks)")
    certification_filter = st.radio("Certification Filter", ["Any", "Certified", "Non-certified"])
    owner_filter = st.text_input("Owner Filter (e.g., Google)")

    # Apply filters
    filtered_courses = filter_courses(user_input, duration_filter, certification_filter, owner_filter)

    # Display filtered courses
    st.header("Filtered Courses")
    if filtered_courses:
        for course in filtered_courses:
            st.write(f"**{course['name']}** - Duration: {course['duration']}, Certification: {course['certification']}, Owner: {course['owner']}")
    else:
        st.warning("No courses match the specified criteria.")

if __name__ == "__main__":
    main()
