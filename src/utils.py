def formatUserData(userdata):
    userdata = userdata.json()
    username = userdata['username']
    faculty = userdata['faculty']
    year = userdata['year']
    nusnet_id = userdata['nusnet_id'].upper()
    formattedData = f"Username: {username}\nFaculty: {faculty}\nYear: {year}\nNUSNET ID: {nusnet_id}"
    return formattedData

def formatAssignmentData(assignmentdata):
    module_code = assignmentdata['module_code'].upper()
    title = assignmentdata['title']
    description = assignmentdata['description']
    file_link = assignmentdata['file_link']
    formattedData = f"Module Code: {module_code}\nTitle: {title}\nDescription: {description}\nSupporting Document: {file_link}"
    return formattedData
