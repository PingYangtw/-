#-----------------------
# 匯入模組
#-----------------------
from flask import Flask, render_template 
from openai import OpenAI
import os
import time

#-----------------------
# 匯入各個服務藍圖
#-----------------------
from services.robott.app import robott_bp
from services.question.app import question_bp

#-------------------------
# 產生主程式, 加入主畫面
#-------------------------
app = Flask(__name__)

#主畫面
@app.route('/')
def index():
    return render_template('/home/home.html') 

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "openai-api-key"))

#json-data
@app.route('/json-data')
def json_data():
    thread = client.beta.threads.create()

    # Create a message to append to our thread
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="營養需求：無糖；餐點時段：午餐；主要食材：馬鈴薯；烹調時間：無要求；特殊飲食需求：素食",
    )

    # Execute our run
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id='asst_vb6Kgql3yMt4FrBWNUGHtwhQ',
    )

    def wait_on_run(run, thread):
        while run.status == "queued" or run.status == "in_progress":
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id,
            )
            time.sleep(0.5)
        return run

    run = wait_on_run(run, thread)

    # Retrieve all the messages added after our last user message
    messages = client.beta.threads.messages.list(
        thread_id = thread.id
    )

    for message in reversed(messages.data):
        data = message.content[0].text.value

    return render_template('/json-data.html',  data=data)

    

#-------------------------
# 在主程式註冊各個服務
#-------------------------
app.register_blueprint(robott_bp, url_prefix='/robott')
app.register_blueprint(question_bp, url_prefix='/question')

#-------------------------
# 啟動主程式
#-------------------------
if __name__ == '__main__':
    app.run(port=5000, debug=True)