import os
import sys
import json
from importlib.resources import path
from urllib import response
from flask import Flask, request, make_response, jsonify, Response
from slack_sdk import WebClient
from dotenv import load_dotenv
import datetime
import gspread
import logging
load_dotenv()

app = Flask(__name__)

# Slack client for Web API requests
client = WebClient(token=os.environ.get('SLACK_BOT_TOKEN'))
channel_id = os.environ.get('CHANNEL_ID')

# Google Sheet connection configuare
ggsheet_concrete = os.path.abspath(os.environ.get('GOOGLE_SHEET_PATH_FILE'))
service_account = gspread.service_account(filename = ggsheet_concrete)
open_service = service_account.open(os.environ.get('GOOGLE_SHEET_NAME'))
work_sheet = open_service.worksheet("Concrete-sheet")

#configuare logfile
logging.basicConfig(filename=os.path.abspath('logs/app_slack.log'), level=logging.DEBUG)

# Dictionary to store coffee orders. In the real world, you'd want an actual key-value store
FORM_DATA = {}

now = datetime.datetime.now()
# client_chat = client.chat_postMessage(channel = "C016ZUZ94DA", text = "Hello")

"""View submission"""
@app.route('/view-submission', methods=['POST'])
def view_submission():
    
    try:
        logging.info('Start view submission')
        payload = json.loads(request.form["payload"])
        FORM_DATA['user_id'] = payload['user']['id']
        FORM_DATA['status'] = 'Chưa xác nhận'
        FORM_DATA['created_at'] = now.strftime("%Y-%m-%d %H:%M")

        if payload["type"] == "view_submission" and payload["view"]["callback_id"] == "apply_for_leave":
            submitted_data = payload["view"]["state"]["values"]

            for data in submitted_data.values():
                start_date_off = start_time_off = end_date_off = end_time_off = ''

                if data.get('form_type'):
                    FORM_DATA['form_type'] = (
                        (data.get('form_type').get('selected_option'))).get('value')
                if (data.get('user_involved')):
                    FORM_DATA['user_involved'] = (data.get('user_involved')).get('selected_user')
                if data.get('reason'):
                    FORM_DATA['reason'] = (data.get('reason')).get('value')
                if data.get('start_date_off'):
                    start_date_off = (data.get('start_date_off')).get('selected_date')
                if data.get('start_time_off'):
                    start_time_off = (data.get('start_time_off')).get('selected_time')
                if data.get('end_date_off'):
                    end_date_off = (data.get('end_date_off')).get('selected_date')
                if data.get('end_time_off'):
                    end_time_off = (data.get('end_time_off')).get('selected_time')

                if start_date_off and start_time_off:
                    FORM_DATA['start_off'] = start_date_off + ' ' + start_time_off

                if end_date_off and end_time_off:
                    FORM_DATA['end_off'] = end_date_off + ' ' + end_time_off
            if FORM_DATA:
                # Send data in google sheet
                googleSheet()

                # Send message
                postMessageWhenUserSubmitForm()
    except:
        logging.error('view submission error')
        
    return Response(), 200

"""Register apply for leave"""
@app.route('/nghiphep', methods=["POST"])
def nghiphep():
    data = request.form
    trigger_id = data.get('trigger_id')

    # Open modal apply for leave
    openModalApplyForLeave(trigger_id)

    return Response(), 200

"""Open modal apply for leave"""
def openModalApplyForLeave(trigger_id):
    hour = now.strftime("%H:%M")
    date = now.strftime("%Y-%m-%d")
    
    return client.views_open(
        trigger_id=trigger_id,
        view={
            "type": "modal",
            "callback_id": "apply_for_leave",
            "title": {
                "type": "plain_text",
                "text": "Concrete-Corp",
                "emoji": True
            },
            "submit": {
                "type": "plain_text",
                "text": "Submit",
                "emoji": True
            },
            "close": {
                "type": "plain_text",
                "text": "Cancel",
                "emoji": True
            },
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "Đăng ký nghỉ phép",
                        "emoji": True
                    }
                },
                {
                    "type": "input",
                    "element":
                        {
                            "type": "static_select",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Lựa chọn hình thức nghỉ phép",
                                "emoji": True
                            },
                            "options": [
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Tự đăng ký",
                                        "emoji": True
                                    },
                                    "value": "Tự đăng ký"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Đăng ký hộ",
                                        "emoji": True
                                    },
                                    "value": "Đăng ký hộ"
                                }
                            ],
                            "action_id": "form_type"
                        },
                    "label": {
                        "type": "plain_text",
                        "text": "Chọn hình thức",
                        "emoji": True
                        }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Nếu đăng ký hộ vui lòng chọn người cần đăng ký ở đây!"
                    },
                    "accessory": {
                        "type": "users_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select a user",
                            "emoji": True
                        },
                        "action_id": "user_involved"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Thời gian bắt đầu*"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "datepicker",
                            "initial_date": date,
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Select a date",
                                "emoji": True
                            },
                            "action_id": "start_date_off"
                        },
                        {
                            "type": "timepicker",
                            "initial_time": hour,
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Select time",
                                "emoji": True
                            },
                            "action_id": "start_time_off"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Thời gian kết thúc*"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "datepicker",
                            "initial_date": date,
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Select a date",
                                "emoji": True
                            },
                            "action_id": "end_date_off"
                        },
                        {
                            "type": "timepicker",
                            "initial_time": hour,
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Select time",
                                "emoji": True
                            },
                            "action_id": "end_time_off"
                        }
                    ]
                },
                {
                    "type": "input",
                    "element": {
                        "type": "plain_text_input",
                        "multiline": True,
                        "action_id": "reason"
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Lý do",
                        "emoji": True
                    }
                }
            ]
        }
    )

"""Submit gooogle sheet"""
def googleSheet():
    # add rows
    try: 
        logging.info('start submit gg sheet')
        user_involved_id = FORM_DATA["user_involved"];
        user_id = FORM_DATA["user_id"]
        data_loop = "'Concrete-Members'!A2:B4"
        user_register = f'=VLOOKUP("{user_id}"; {data_loop}; 2; FALSE)' if user_id is not None else None;
        user_involved = f'=VLOOKUP("{user_involved_id}"; {data_loop}; 2; FALSE)' if user_involved_id is not None else None;
        
        work_sheet.append_row([
            FORM_DATA['created_at'],
            user_register,
            FORM_DATA['form_type'],
            user_involved,
            FORM_DATA['start_off'],
            FORM_DATA['end_off'],
            FORM_DATA['reason'],
            FORM_DATA['status'],
        ], value_input_option='USER_ENTERED')
        
        return True;
    except:
        logging.error('submit gg sheet error')
        return False;

"""Post message Slack When user submit form"""
def postMessageWhenUserSubmitForm():
    user_involved = f"- <@{FORM_DATA['user_involved']}>" if FORM_DATA['user_involved'] is not None else ''
    client.chat_postMessage(
        channel=channel_id,
        attachments=[
            {
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"Đơn xin nghỉ phép:\n*<@{FORM_DATA['user_id']}>* CC <!channel>"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Ngày bắt đầu:*\n{FORM_DATA['start_off']}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Ngày kết thúc:*\n{FORM_DATA['end_off']}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Hình thức:*\n{FORM_DATA['form_type']} {user_involved}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Reason:*\n{FORM_DATA['reason']}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Ngày tạo đơn:*\n{FORM_DATA['created_at']}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": "*Trạng thái:*\nĐơn xin phép của đã gửi đến bộ phận nhân sự."
                            }
                        ]
                    }
                ]
            }
        ]
    )

if __name__ == "__main__":
    # app.run("localhost", 3000, debug=True)
    app.run()
