def formatUserData(userdata):
    userdata = userdata.json()
    username = userdata['username']
    faculty = userdata['faculty']
    year = userdata['year']
    nusnet_id = userdata['nusnet_id'].upper()
    formattedData = f"Username: {username}\nFaculty: {faculty}\nYear: {year}\nNUSNET ID: {nusnet_id}"
    return formattedData
