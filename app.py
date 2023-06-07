from flask import Flask,Response,render_template
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
import aiohttp
import re
import time
import threading
import requests
import hashlib
import itertools
import schedule
import json

app = Flask(__name__)
scheduler = BackgroundScheduler(daemon=True)
is_running = False
flagsString=""
status="solving"
lastFetched=datetime.now()
next_event=datetime.now()
switch=0
time_remaining=0
seconds_remaining=0
# status="Not running the script"


@app.route('/')
def index():
    # if not scheduler.running:
    #     print("hii")
    #     # solver()
    #     scheduler.add_job(run_script, 'interval', minutes=30,id='solver',next_run_time=datetime.now())
    #     scheduler.start()
    
    return render_template('index.html')



def generate_logs():
    def log_generator():
        global status
        global flagsString

        while True:
            data = {
                    'status': status,
                    'flags': flagsString
                }
            
            json_data = json.dumps(data)
            
            yield 'data: {}\n\n'.format(json_data)
            time.sleep(1)

    return Response(log_generator(), mimetype='text/event-stream')





def solver():
    
        global flagsString
        global lastFetched
        global status
        global switch
        global is_running
        is_running=True
        switch=1
    # with app.app_context():
    # while True:
       
        
        status="Solving"

        url= "https://0ijq1i6sp1.execute-api.us-east-1.amazonaws.com/dev/"
        flags=[]

        
        # yield 'data: Script Started\n\n'
        # browser
        def get_browser():
            global status
            pattern = r'Mozilla\/[\d\.]+\s\(.*?\) AppleWebKit\/[\d\.]+\s\(KHTML, like Gecko\) Version\/[\d\.]+\sSafari\/[\d\.]+'
            status="Finding the first flag"
            # yield 'data: Finding the first flag\n\n'
            
            print("\nFinding the first Flag")
            browserReq= requests.get(url+'browser')
            # status="got req"
            user_agent = re.search(pattern, browserReq.json()).group()
            # status="got user-agent"
            headers = {"User-Agent": user_agent}
            flag1 = requests.get(url+'browser', headers=headers)
            # status="got first flag"
            if flag1.json():
                print("Found the first flag")
                # yield 'data: found first flag\n\n'
                flags.append(flag1.json())
                status="got first flag"

            


        #hash
        def get_hash():
            global status
            print("\nDecrypting the MD5 hash")
            # yield 'data: decrypting md5 hash\n\n'
            hashReq=requests.get(url+'hash')
            pattern = r"md5\(flag\+salt\):[a-f0-9]+:"
            pattern2 = r"md5\(flag\+salt\):([^:]+):"
            status="finding second flag"

            match = re.search(pattern2, hashReq.json())
            if match:
                md5 = match.group(1)


            salt = re.sub(pattern, "", hashReq.json())



            def encrypt_with_salt(word, salt):
                salted_word = word + salt
                hashed_word = hashlib.md5(salted_word.encode()).hexdigest()
                return hashed_word

            def compare_encrypted_value(word, salt, encrypted_value):
                hashed_word = encrypt_with_salt(word, salt)
                return hashed_word == encrypted_value

            # Provide the salt and encrypted value to compare against

            encrypted_value_to_compare = md5  # Example encrypted value for the word "password"
            status="decrypting md5 hash"
            # Read words from file and compare encrypted values
            with open("list.txt", "r") as file:
                for word in file:
                    word = word.strip()  # Remove leading/trailing whitespaces
                    encrypted_word = encrypt_with_salt(word, salt)
                    if compare_encrypted_value(word, salt, encrypted_value_to_compare):
                        print("Found the second flag")
                        status="found second flag"
                        # yield 'data: found the second flag\n\n'
                        flags.append(word)


        # exception
        def get_exception():
            global status
            status="finding third flag"
            # yield 'data: finding the third flag\n\n'
            print("\nFinding the third flag")
            exceptionReq=requests.get(url+"exception?q=tqaaaaa")
            if exceptionReq.json():
                print("Third flag found")
                status="found third flag"
                # yield 'data: found the third flag\n\n'
                flags.append(exceptionReq.json())


        #stream
        def get_stream():
            global status
            tmpRes=set()
            status="finding fourth flag"
            # yield 'data: finding fourth flag\n\n'
            print("\nFinding last flag")
            print("Fetching stream characters")
            status="fetching stream characters"

            def get_tasks(session):
                global status
                status="getting tasks"
                tasks=[]
                for i in range(350):
                    status="inside task loop"
                    tasks.append(session.get(url+"stream"))
                    status="inside task loop 2"
                return tasks
                
            async def get_stream_char():
                global status
                async with aiohttp.ClientSession() as session:
                    tasks=get_tasks(session)
                    responses=await asyncio.gather(*tasks)
                    for response in responses:
                       
                        res_char= await response.json()
                        try:
                            tmpRes.add(res_char)
                            
                            print(res_char)
                        except TypeError:
                            continue

                    
                        


            asyncio.run(get_stream_char())
            status="all char added"
            # yield 'data: all char found\n\n'




            # for i in range(100):
            #     if(len(tmpRes)==7):
            #         print("already found all")
            #         break
            #     request=requests.get(url+"stream")
            #     status= ("Still finding the last flag | " +str(i)+" characters fetched")
            #     print(str(i))
            #     tmpRes.add(request.json())



            print("Done fetching")
            status="done fetching stream characters"
            # yield 'data: done  fetching\n\n'
            # print(tmpRes)

            def find_dictionary_word(characters, word_list_file):
                # Generate all possible permutations of the characters
                permutations = [''.join(p) for p in itertools.permutations(characters)]
                
                # Read the words from the word list file
                with open(word_list_file, 'r') as file:
                    word_list = file.read().splitlines()
                    # print(word_list)
                
                # Iterate through the permutations and check if they exist in the word list
                
                for word in permutations:
                    # print(word)
                    if word in word_list:
                    
                        return word
                
                # If no word is found
                return None


            # Set of characters
            characters = tmpRes

            # File path of the word list
            word_list_file = 'list.txt'

            # Find a word from the characters
            result = find_dictionary_word(characters, word_list_file)

            if result:
                # print("Word found:", result)
                status="last flag found"
                print("Last flag found")
                # yield 'data: fourth flag found\n\n'
                flags.append(result)
            else:

                print("No word found.")

        get_browser()
       
        get_hash()
        
        get_exception()
        get_stream()

        flagsString = ', '.join(flags)
        lastFetched=datetime.now()
        
        status="script completed | all flags found"
        is_running=False
        
    
        # yield f'data: {flagsString}\n\n'
        
        # time.sleep(30*60)
        # switch=0
        
def run_script():
    global status
    # is_running = any(threading.current_thread().target == solver for thread in threading.enumerate())

    if is_running:
        status="script is already running"

        print("A thread for solver is already running.")
    else:
        status="script initialized"
        print("No thread for solver is currently running.")
        thread = threading.Thread(target=solver,daemon=True)
        thread.start()








@app.route('/logs')
def logs():
    run_script()
    total_threads = threading.active_count()

    print("Total number of active threads:", total_threads)
    return generate_logs()

if __name__ == '__main__':
    app.run(debug=True)
