import enum
import mimetypes
import uuid

import streamlit as st
import os
import pandas as pd
import streamlit_authenticator as stauth
import yaml
import dataclasses


########### Monkey Patch, should be resolved in stremlit-authenticator 0.3.4
# https://github.com/mkhorasani/Streamlit-Authenticator/issues/187
from streamlit_authenticator.utilities import Validator


def validate_password(self, password):
    if 6 < len(password) < 21:
        return True
    return False


Validator.validate_password = validate_password
############
CFG_DIRECTORY = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data'))
with open(os.path.join(CFG_DIRECTORY, 'config.yaml')) as file:
    config = yaml.safe_load(file)

if 'media' not in config.keys() or not isinstance(config['media'], list):
    config['media'] = []

DATA_DIRECTORY = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data'))
MEDIA_DIRECTORY = config.get('default_media_dir', DATA_DIRECTORY)

st.set_page_config(
    page_title="InfoboardPI",
    page_icon="📊",
    layout='wide',
    initial_sidebar_state="expanded")

st.markdown("""
    <style>
        
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
        [data-testid="stAppViewBlockContainer"] {
            padding-top: 1.5em;
        }
    </style>
""", unsafe_allow_html=True)


authenticator = stauth.Authenticate(config['server']['credentials'],
                                    config['server']['cookie']['name'],
                                    config['server']['cookie']['key'],
                                    config['server']['cookie']['expiry_days'],
                                    validator=Validator()
                                    )


def set_width(width: str = '750px'):
    css = f'<style>' \
          f'   section.main > div {{max-width:{width}}}' \
          f'</style>'
    st.markdown(css, unsafe_allow_html=True)

def set_centered():
    css = f'<style>' \
          f'   section.main > div {{text-align: center}}' \
          f'</style>'
    st.markdown(css, unsafe_allow_html=True)

def login():
    pass

def check_login():
    name, authentication_status, username = authenticator.login('main')

    if authentication_status == False:
        st.error('Username/password is incorrect')

    return authentication_status

def logout():
    # authenticator = stauth.Authenticate(config['credentials'],
    #                                     config['cookie']['name'],
    #                                     config['cookie']['key'],
    #                                     config['cookie']['expiry_days'],
    #                                     )

    authenticator.authentication_controller.logout()
    authenticator.cookie_controller.delete_cookie()
    st.rerun()


def list_parquet_files(directory):
    files = [''] + [f for f in os.listdir(directory) if f.endswith('.parquet')]
    return files



# search = st.Page("tools/search.py", title="Search", icon=":material/search:")
# history = st.Page("tools/history.py", title="History", icon=":material/history:")

class MediaTypes(enum.Enum):
    IMAGE = 1
    VIDEO = 2

@dataclasses.dataclass
class Media:
    url: str = None
    real_url: str = None
    slide_time: int = None
    valid: bool = True
    type: MediaTypes = None

    def __post_init__(self):
        if not os.path.isfile(self.url):
            if os.path.isfile(os.path.join(MEDIA_DIRECTORY, self.url)):
                self.real_url = os.path.join(MEDIA_DIRECTORY, self.url)
            else:
                self.valid = False
        else:
            self.real_url = self.url

        mime = mimetypes.guess_type(self.url)[0]
        if mime is not None:
            if mime.startswith('image'):
                self.type = MediaTypes.IMAGE
            elif mime.startswith('video'):
                self.type = MediaTypes.VIDEO
            else:
                self.valid = False
        else:
            self.valid = False

def get_media() -> list[Media]:
    media_list = []
    for media in config['media']:
        if isinstance(media, dict):
            media_data = Media(**media)
            if media_data.valid:
                media_list.append(media_data)

    return media_list

def update_config_yaml():
    with open(os.path.join(CFG_DIRECTORY, 'config.yaml'), 'w') as file:
        yaml.dump(config, file, default_flow_style=False)

def update_media_config(media_list):
    new_media_list = []
    for media in media_list:
        new_media_list.append({'url': media.url,
                               'slide_time': media.slide_time})
    config['media'] = new_media_list

def viewer():
    set_centered()
    st.title('Slideshow list')
    st.session_state.setdefault('uploader_key', uuid.uuid4())

    media_list = get_media()

    uploaded_file = st.file_uploader("Upload file", accept_multiple_files=False, key=st.session_state.uploader_key)

    if uploaded_file:
        mime = uploaded_file.type
        if mime is None or ( not mime.startswith('image') and not mime.startswith('video')):
            st.error(f'File {uploaded_file.name} is probably not image or video. Guessed mime type is {mime}')
        else:
            name = uploaded_file.name
            if os.path.isfile(os.path.join(MEDIA_DIRECTORY, name)):
                iter = 0
                splitted_name = name.split('.')
                new_name = name
                while os.path.isfile(os.path.join(MEDIA_DIRECTORY, new_name)):
                    new_name = f'{".".join(splitted_name[:-1])}_({iter}).{splitted_name[-1]}'
                    iter += 1
                name = new_name

            data = uploaded_file.getbuffer()
            with open(os.path.join(MEDIA_DIRECTORY, name), 'wb') as f:
                f.write(data)
            media_list.append(Media(name, slide_time=config.get('default_slide_time', 60)))
            update_media_config(media_list)
            update_config_yaml()
            media_list = get_media()
            st.success(f'File uploaded as {name}')
        st.session_state.pop('uploader_key')

    for pos, media in enumerate(media_list):
        c = st.container(border=True)
        cols = c.columns([0.6, 0.2, 0.2], vertical_alignment='center')
        cols[0].write(f'{media.url}')
        if media.type == MediaTypes.IMAGE:
            cols_timing = cols[1].columns([0.3, 0.5, 0.1], vertical_alignment='center')
            cols_timing[0].write(f':material/timer:')
            number = cols_timing[1].number_input('Timing', label_visibility='collapsed', key=f'timing_{pos}', value=int(media.slide_time), min_value=1)
            if number != int(media.slide_time):
                media.slide_time = number
                update_media_config(media_list)
                update_config_yaml()
            cols_timing[2].write(f's')
        cols_buttons = cols[2].columns([0.33, 0.33, 0.33])
        if pos != 0:
            if cols_buttons[0].button(':material/north:', key=f'up_{media.url}',  use_container_width=True):
                media_list.insert(pos-1, media_list.pop(pos))
                update_media_config(media_list)
                update_config_yaml()
                st.rerun()

        if pos != len(media_list) - 1:
            if cols_buttons[1].button(':material/south:', key=f'down_{media.url}',  use_container_width=True):
                media_list.insert(pos + 1, media_list.pop(pos))
                update_media_config(media_list)
                update_config_yaml()
                st.rerun()
        if cols_buttons[2].button(':material/delete_forever:', key=f'delete_{media.url}',  use_container_width=True):
            cols_delete = c.columns([0.5, 0.5])
            cols_delete[0].button(f'Cancel', type='primary', use_container_width=True)
            cols_delete[1].button(f'Delete {media.url} permanently', on_click=delete_media, args=[media.real_url], use_container_width=True)

def delete_media(url):
    os.remove(url)
    media_list = get_media()
    update_media_config(media_list)
    update_config_yaml()

def user_edit_user():
    if st.session_state['authentication_status']:
        try:
            # if authenticator.update_user_details(st.session_state['username']):
            #     st.success('Entries updated successfully')
            #     with open(os.path.join(os.path.dirname(__file__), 'config.yaml'), 'w') as file:
            #         yaml.dump(config, file, default_flow_style=False)
            if authenticator.reset_password(st.session_state['username']):
                st.success('Password updated successfully')
                update_config_yaml()
        except Exception as e:
            st.error(e)

login_page = st.Page(login, title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
viewer_page = st.Page(viewer, title="Slideshow List", icon=":material/slideshow:")
edit_user_page = st.Page(user_edit_user, title="Edit account", icon=":material/manage_accounts:")

if check_login():
    pages = {}
    pages['Infoboard'] = [viewer_page]
    pages['Account'] = [edit_user_page, logout_page]

    pg = st.navigation(pages)
    pg.run()

else:
    pg = st.navigation([login_page])
    pg.run()
