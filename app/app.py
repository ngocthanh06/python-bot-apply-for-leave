from ast import parse
from importlib.resources import path
import logging
from re import I
import sys
import os
from numpy import identity
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import json
import pprint
from dotenv import load_dotenv
from flask import Flask, request
import gspread

load_dotenv()

ggsheet_concrete = os.path.abspath(os.environ.get('GOOGLE_SHEET_PATH_FILE'))

sa = gspread.service_account(filename = ggsheet_concrete)
sp = sa.open(os.environ.get('GOOGLE_SHEET_NAME'))

class App:
    client = WebClient(token = os.environ.get("SLACK_USER_TOKEN"))
    channel_name = os.environ.get("SLACK_CHANNEL_NAME")
    channel_id = os.environ.get("CHANNEL_ID")
    logger = logging.getLogger(__name__)
    
    def __init__(self):
        pass
    
    def demo(self):
        
        # print(self.client.rtm_connect(token=os.environ.get("SLACK_BOT_TOKEN")))
        
        
        # conversations_channel = self.get_conversation_in_channel();
        
        # conversations_history = self.client.conversations_history(channel=self.channel_id)
        
        # message = {}
        
        # for key, val in enumerate(conversations_history['messages']):
        #     message[key] = val
        
        # print(json.dumps(message, indent=4, sort_keys=True))
        
        members = self.client.conversations_members(channel = 'C016ZUZ94DA');
        
        print(members);
        
    """ get members in slack """
    def get_members_in_slack(self, users_array : list) -> dict:
        members_slack = {}
        
        for key, user in enumerate(users_array):
            members_slack[key] = user
            
        return members_slack;
    
    """ get conversation in channel """
    def get_conversation_in_channel(self):
        return self.client.conversations_info(channel=self.channel_id)['channel'];
    
    """ save members in slack to gg sheet """
    def save_members_in_slack_to_gg_sheet(self):
        try:
            # handle save save members in google sheets
            user_list = self.client.users_list()['members'];
            
            members_slack = self.get_members_in_slack(user_list)
            
            MEMBERS = [];
            for member in members_slack.values():
                if member['is_bot'] is False and member['id'] != 'USLACKBOT':
                    MEMBERS.append([ member['id'], member['name'] ]);
            # print(json.dumps(members_slack, indent=4, sort_keys=True))
            ws = sp.worksheet('Concrete-Members');
            
            # add rows
            ws.append_rows(MEMBERS, value_input_option = 'RAW')
            return True;
        except:
            print('err');
        
        
app = App()
app.save_members_in_slack_to_gg_sheet()
    