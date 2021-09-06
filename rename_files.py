import glob
import os
from datetime import datetime, timedelta

i = 0
for file_name_old in glob.glob("data\\demo\\*.xyz"):
    
    # Print old file_name
    print(file_name_old)
    
    # Get only name with path and extension
    file_name_without_ext = os.path.splitext(file_name_old)[0]
    file_name_without_path = os.path.basename(file_name_old)
    file_name_without_path_and_ext = os.path.splitext(file_name_without_path)[0]
    
    # Count survey
    i = i + 1

    # Generate survey_type
    if file_name_without_ext in ['H04805','H07140','H08938','H09063','H09064','H07127','H00741A','H00741B','H03032']:
        survey_type = 'SB'
    else:
        survey_type = 'MB'

    # Generate date and cast to string
    survey_date = datetime.date(datetime.now()) - timedelta(i * 20)

    # Set survey company
    if i % 2 == 0 :
        survey_organisation = 'NOAA'
    else :
        survey_organisation = 'Fugro'

    # Set new metadata file_name
    metadata_file_name = os.path.splitext(file_name_old)[0] + '_metadata.txt'

    # Open new file
    print(metadata_file_name)
    fOut = open(metadata_file_name,'w')

    # Write metadata
    fOut.write('name: ' + str(file_name_without_path_and_ext) + '\n')
    fOut.write('date: ' + str(survey_date.strftime("%Y%m%d")) + '\n')
    fOut.write('type: ' + str(survey_type) + '\n')
    fOut.write('contractor: ' + str(survey_organisation) + '\n')

    # Close file
    fOut.close()