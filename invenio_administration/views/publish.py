import json
import os
import requests
from .model import *

api = "https://127.0.0.1:5000"
token = "m1VuHtbNzvxjZuLfBs8PeIVsnAEETt31K2gnmPwKVQxZyOi7BZruP1iO0klT"


h = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
    }
fh = {
    "Accept": "application/json",
    "Content-Type": "application/octet-stream",
    "Authorization": f"Bearer {token}"
    }

def publish_function():
    files = session.query(OriginalFile).filter_by(file_type='pdf')   

    for original_file in files:
        files_list=[]
        creators_list=[]
        description = ''
        additional_descriptions=[]
        identifier=''
        publdate=''
        publisher=''
        contributors_list=[]
        restype=''
        rights_list=[]
        subjects_list=[]
        rectitle=''
        additional_titles=[]
        searchability=''

        arabic_records = session.query(ArabicFile).filter_by(original_file_id=original_file.id)  
        french_records = session.query(FrenchFile).filter_by(original_file_id=original_file.id)  
        spanish_records = session.query(SpanishFile).filter_by(original_file_id=original_file.id)   
        english_records = session.query(EnglishFile).filter_by(original_file_id=original_file.id)  
        original_file_name = original_file.file_name
        files_list.append(f'{original_file_name}.pdf')

        for arabic_record in arabic_records:
            file_name = arabic_record.file_name
            file_path =f"{file_name}.pdf.docx"
            files_list.append(file_path)
        
        for french_record in french_records:
            file_name = french_record.file_name
            file_path =f"{file_name}.pdf.docx"
            files_list.append(file_path)
        
        for spanish_record in spanish_records:
            file_name = spanish_record.file_name
            file_path = f"{file_name}.pdf.docx"
            files_list.append(file_path)
        
        for english_record in english_records:
            file_name = english_record.file_name
            file_path = f"{file_name}.pdf.docx"
            files_list.append(file_path)


        arabic_metadatas = session.query(ArabicMetadata).filter_by(original_file_id=original_file.id)  
        french_metadatas = session.query(FrenchMetadata).filter_by(original_file_id=original_file.id)  
        spanish_metadatas = session.query(SpanishMetadata).filter_by(original_file_id=original_file.id)   
        english_metadatas = session.query(EnglishMetadata).filter_by(original_file_id=original_file.id)  
        original_metadatas = session.query(OriginalFile).filter_by(id=original_file.id)

        for original_metadata in original_metadatas:
            metadata_dict = original_metadata.metadata_file
            json_data = json.dumps(metadata_dict)
            data=json.loads(json_data.encode('utf-8'))
            creators_info = data.get('metadata', {}).get('creators', [])
            for author in creators_info:
                person_or_org = author.get('person_or_org',{})
                family_name = person_or_org.get('family_name','') 
                creator={
                        "person_or_org":{
                            "family_name": family_name,
                            "type": "personal"                                                                        
                        }
                        }
                creators_list.append(creator)
            description = data.get('metadata', {}).get('description','')
            get_identifier = data.get('metadata', {}).get('identifiers', [])
            for id in get_identifier:
                identifier = id.get('identifier','') 
            publdate = data.get('metadata', {}).get('publication_date','')
            publisher += data.get('metadata', {}).get('publisher','') + "  "
            get_contributor = data.get('metadata', {}).get('contributors', [])
            for contribute in get_contributor:
                try:
                    person_or_org = contribute.get('person_or_org',{})
                    contributor_name = person_or_org.get('name','') 
                    contributor={
                            "person_or_org":{
                                "type": "personal",
                                "name": contributor_name,
                                "family_name": contributor_name
                            },
                            "role": {
                                "id": "other"
                            }
                            }
                    contributors_list.append(contributor)
                except:
                    contributors_list =[]
            get_resource = data.get('metadata', {}).get('resource_type', {})
            restype=get_resource.get('id','')
            get_rights = data.get('metadata', {}).get('rights', [])
            for right in get_rights:
                rights_list.append(right)
            get_subject = data.get('metadata', {}).get('subjects', [])
            for subject in get_subject:
                subjects_list.append(right)
            rectitle = data.get('metadata', {}).get('title','')
            

        for arabic_metadata in arabic_metadatas:
            file_name = arabic_metadata.file_name
            file_path = f'{file_name}.json'
            # files_list.append(file_path)
            with open(file_path, 'r', encoding='utf-8') as file:
                json_content = file.read()
            data = json.loads(json_content)
            creators_info = data.get('metadata', {}).get('creators', [])
            rights_info = data.get('metadata', {}).get('rights', [])
            get_description = data.get('metadata', {}).get('description')
            add_description = {
                            "description": get_description,
                            "type": {"id": "other",}
                            }
            additional_descriptions.append(add_description)
            
            for author in creators_info:
                person_or_org = author.get('person_or_org',{})
                family_name = person_or_org.get('family_name','') 
                creator={
                        "person_or_org":{
                            "family_name": family_name,
                            "type": "personal"                                                                        
                        }
                        }
                creators_list.append(creator)
            publisher += data.get('metadata', {}).get('publisher') + "  "
            get_contributor = data.get('metadata', {}).get('contributors', [])
            for contribute in get_contributor:
                try:
                    person_or_org = contribute.get('person_or_org',{})
                    contributor_name = person_or_org.get('name','') 
                    contributor={
                            "person_or_org":{
                                "type": "personal",
                                "name": contributor_name,
                                "family_name": contributor_name
                            },
                            "role": {
                                "id": "other"
                            }
                            }
                    contributors_list.append(contributor)
                except:
                    contributors_list =[]

            get_rights = data.get('metadata', {}).get('rights', [])
            for right in get_rights:
                rights_list.append(right)
            get_title = data.get('metadata', {}).get('title','')
            add_title = {
                        "title": get_title,
                        "type": {
                            "id": "alternative-title",}
                        }
            additional_titles.append(add_title)


        for french_metadata in french_metadatas:
            file_name = french_metadata.file_name
            file_path = f'{file_name}.json'
            # files_list.append(file_path)
            with open(file_path, 'r', encoding='utf-8') as file:
                json_content = file.read()
            data = json.loads(json_content)
            creators_info = data.get('metadata', {}).get('creators', [])
            rights_info = data.get('metadata', {}).get('rights', [])
            get_description = data.get('metadata', {}).get('description')
            add_description = {
                            "description": get_description,
                            "type": {"id": "other",}
                            }
            additional_descriptions.append(add_description)
            
            for author in creators_info:
                person_or_org = author.get('person_or_org',{})
                family_name = person_or_org.get('family_name','') 
                creator={
                        "person_or_org":{
                            "family_name": family_name,
                            "type": "personal"                                                                        
                        }
                        }
                creators_list.append(creator)
            publisher += data.get('metadata', {}).get('publisher') + "  "
            get_contributor = data.get('metadata', {}).get('contributors', [])
            for contribute in get_contributor:
                try:
                    person_or_org = contribute.get('person_or_org',{})
                    contributor_name = person_or_org.get('name','') 
                    contributor={
                            "person_or_org":{
                                "type": "personal",
                                "name": contributor_name,
                                "family_name": contributor_name
                            },
                            "role": {
                                "id": "other"
                            }
                            }
                    contributors_list.append(contributor)
                except:
                    contributors_list =[]
            get_rights = data.get('metadata', {}).get('rights', [])
            for right in get_rights:
                rights_list.append(right)
            get_title = data.get('metadata', {}).get('title','')
            add_title = {
                        "title": get_title,
                        "type": {
                            "id": "alternative-title",}
                        }
            additional_titles.append(add_title)

        for spanish_metadata in spanish_metadatas:
            file_name = spanish_metadata.file_name
            file_path = f'{file_name}.json'
            # files_list.append(file_path)
            with open(file_path, 'r', encoding='utf-8') as file:
                json_content = file.read()
            data = json.loads(json_content)
            creators_info = data.get('metadata', {}).get('creators', [])
            rights_info = data.get('metadata', {}).get('rights', [])
            get_description = data.get('metadata', {}).get('description')
            add_description = {
                            "description": get_description,
                            "type": {"id": "other",}
                            }
            additional_descriptions.append(add_description)
            
            for author in creators_info:
                person_or_org = author.get('person_or_org',{})
                family_name = person_or_org.get('family_name','') 
                creator={
                        "person_or_org":{
                            "family_name": family_name,
                            "type": "personal"                                                                        
                        }
                        }
                creators_list.append(creator)
            publisher += data.get('metadata', {}).get('publisher') + "  "
            get_contributor = data.get('metadata', {}).get('contributors', [])
            for contribute in get_contributor:
                try:
                    person_or_org = contribute.get('person_or_org',{})
                    contributor_name = person_or_org.get('name','') 
                    contributor={
                            "person_or_org":{
                                "type": "personal",
                                "name": contributor_name,
                                "family_name": contributor_name
                            },
                            "role": {
                                "id": "other"
                            }
                            }
                    contributors_list.append(contributor)
                except:
                    contributors_list =[]
            get_rights = data.get('metadata', {}).get('rights', [])
            for right in get_rights:
                rights_list.append(right)
            get_title = data.get('metadata', {}).get('title','')
            add_title = {
                        "title": get_title,
                        "type": {
                            "id": "alternative-title",}
                        }
            additional_titles.append(add_title)            

        for english_metadata in english_metadatas:
            file_name = english_metadata.file_name
            file_path = f'{file_name}.json'
            # files_list.append(file_path)
            with open(file_path, 'r', encoding='utf-8') as file:
                json_content = file.read()
            data = json.loads(json_content)
            creators_info = data.get('metadata', {}).get('creators', [])
            rights_info = data.get('metadata', {}).get('rights', [])
            get_description = data.get('metadata', {}).get('description')
            add_description = {
                            "description": get_description,
                            "type": {"id": "other",}
                            }
            additional_descriptions.append(add_description)
            
            for author in creators_info:
                person_or_org = author.get('person_or_org',{})
                family_name = person_or_org.get('family_name','') 
                creator={
                        "person_or_org":{
                            "family_name": family_name,
                            "type": "personal"                                                                        
                        }
                        }
                creators_list.append(creator)
            publisher += data.get('metadata', {}).get('publisher') + "  "
            get_contributor = data.get('metadata', {}).get('contributors', [])
            for contribute in get_contributor:
                try:
                    person_or_org = contribute.get('person_or_org',{})
                    contributor_name = person_or_org.get('name','') 
                    contributor={
                            "person_or_org":{
                                "type": "personal",
                                "name": contributor_name,
                                "family_name": contributor_name
                            },
                            "role": {
                                "id": "other"
                            }
                            }
                    contributors_list.append(contributor)
                except:
                    contributors_list =[]
            get_rights = data.get('metadata', {}).get('rights', [])
            for right in get_rights:
                rights_list.append(right)
            get_title = data.get('metadata', {}).get('title','')
            add_title = {
                        "title": get_title,
                        "type": {
                            "id": "alternative-title",}
                        }
            additional_titles.append(add_title)            

            
        datameta = {
                    "access": {
                        "files": "public",
                        "record": "public"
                    },
                    "files": {
                        "enabled": True
                    },
                    "metadata": {
                        "creators": creators_list,
                        "description": description,

                        "additional_descriptions": additional_descriptions,
                        "identifiers": [{
                        "identifier": identifier,
                        "scheme": "other"
                        }],
                        "publication_date": publdate,
                        "publisher": publisher,
                        "contributors": contributors_list,
                        "resource_type": {
                        "id": restype
                        },
                        "rights": rights_list,
                        "subjects": subjects_list,
                        "title": rectitle,
                        "additional_titles": additional_titles,
                        "version": "v1"
                    },
                    "custom_fields": {
                        "invisible_search": searchability
                    },
                    "pids": {}
                    }


        r = requests.post(
            f"{api}/api/records", data=json.dumps(datameta), headers=h, verify=False)
        assert r.status_code == 201, \
            f"Failed to create record (code: {r.status_code})"
        links = r.json()['links']
        # Upload files
        # print("File upload")
        # print(links)
        file_api=links['files']

    # 'content': 'https://127.0.0.1:5000/api/records/x42hh-63508/draft/files/The327875.pdf/content', 
    # 'commit': 'https://127.0.0.1:5000/api/records/x42hh-63508/draft/files/The327875.pdf/commit'

        # print(files_list)
        for file_upload in files_list:
            f = file_upload
            # Initiate the file
            data = json.dumps([{"key": f}])
            r = requests.post(links["files"], data=data, headers=h, verify=False)
            assert r.status_code == 201, \
                f"Failed to create file {f} (code: {r.status_code})"
            file_links = r.json()["entries"][0]["links"]
            print("FILE LINKS")
            print(file_links)

            # Upload file content by streaming the data
            # with open(f, 'rb') as fp:
            with open(f, 'rb') as fp:
                r = requests.put(
                    f"{file_api}/{f}/content", data=fp, headers=fh, verify=False)
            assert r.status_code == 200, \
                f"Failed to upload file content {f} (code: {r.status_code})"

            # Commit the file.
            r = requests.post(f"{file_api}/{f}/commit", headers=h, verify=False)
            assert r.status_code == 200, \
                f"Failed to commit file {f} (code: {r.status_code})"

        # Publish the record
        r = requests.post(links["publish"], headers=h, verify=False)
        assert r.status_code == 202, \
                f"Failed to publish record (code: {r.status_code})"



