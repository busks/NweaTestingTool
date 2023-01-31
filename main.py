import threading, requests, colorama, json, random
import os

config = json.load(open('input/config.json', 'r'))
proxies = [proxy.strip() for proxy in open('input/proxies.txt', 'r').readlines()] # Proxies Are Not Needed

class MAP():
      def __init__(self, proxy: str = None) -> None:
          self.endpoint = 'test.mapnwea.org/proctor'
          self.proxy = ({
               'http'  : 'http://%s' % (proxy),
               'https' : 'http://%s' % (proxy),
          } if proxy != None else None)

      def joinTestSession(self, sessionName: str, sessionPass: str) -> requests.Response:
          return requests.post(
               f'https://{self.endpoint}/joinTestSession',
                 json = {
                      'testSessionName': sessionName,
                      'testSessionPassword': sessionPass,
                 }, proxies = self.proxy,
          )

      def setReadyToConfirm(self, sessionPass: str, assignedTestId: str,  assignedTestName: str, studentId: str, authToken: str) -> requests.Response:
          return requests.post(
               f'https://{self.endpoint}/setStudentReadyToBeConfirmed',
                 headers = {'Auth-Token': authToken},
                 json = {
                      'studentBid': studentId,
                      'testSessionId': assignedTestId,
                      'assignedOrChosenTest': {
                              'testKey': sessionPass,
                              'testName': assignedTestName,
                      }
                 }, proxies = self.proxy,
          )

http = MAP(random.choice(proxies) if len(proxies) != 0 else None)
sessionName = input(f'{colorama.Fore.GREEN}{colorama.Style.BRIGHT}!{colorama.Style.RESET_ALL} Session Name: ')
sessionPass = input(f'{colorama.Fore.GREEN}{colorama.Style.BRIGHT}!{colorama.Style.RESET_ALL} Session Pass: ')
test = http.joinTestSession(sessionName, sessionPass)

if test.json().get('errorMessage') == 'NOT_AUTHORIZED':
   print(f'{colorama.Fore.RED}{colorama.Style.BRIGHT}!{colorama.Style.RESET_ALL} Invalid Session Name Or Password')
else:  
    while True:
          os.system('clear || cls')
          print('🗺')
          print(f'{colorama.Fore.GREEN}{colorama.Style.BRIGHT}1{colorama.Style.RESET_ALL} :: Scrape Student {colorama.Fore.LIGHTBLUE_EX}{colorama.Style.BRIGHT}IDs{colorama.Style.RESET_ALL} & Student {colorama.Style.BRIGHT}{colorama.Fore.LIGHTBLUE_EX}Names{colorama.Style.RESET_ALL}')
          print(f'{colorama.Fore.GREEN}{colorama.Style.BRIGHT}2{colorama.Style.RESET_ALL} :: Set All Students Ready')
          x = input('  >> ')
    
          if x == '1':
             try:
                req = http.joinTestSession(sessionName, sessionPass)
                print(f'{colorama.Fore.GREEN}{colorama.Style.BRIGHT}!{colorama.Style.RESET_ALL} Extracting {colorama.Style.BRIGHT}{colorama.Fore.LIGHTBLUE_EX}%s{colorama.Style.RESET_ALL} Students' % (len(req.json()['clientTestSessionDo']['studentSessionList'])))
                for student in req.json()['clientTestSessionDo']['studentSessionList']:
                    try:
                        print(f'{colorama.Fore.GREEN}{colorama.Style.BRIGHT}*{colorama.Style.RESET_ALL} Extracted (s{colorama.Style.BRIGHT}{colorama.Fore.LIGHTBLUE_EX}{student["studentNumber"]}{colorama.Style.RESET_ALL}, {student["studentNameFirst"]} {student["studentNameLast"]})')
                        open('output/students.txt', 'a+').write(f'{student["studentNumber"]}:{student["studentNameFirst"]}:{student["studentNameLast"]}\n')
                    except KeyError as Key:
                           print(f'{colorama.Fore.RED}{colorama.Style.BRIGHT}*{colorama.Style.RESET_ALL} Cannot Extract Student, JSON Key Not Found %s' % (Key))
                    except Exception as E:
                           print(f'{colorama.Fore.RED}{colorama.Style.BRIGHT}*{colorama.Style.RESET_ALL} Cannot Extract Student')
             except Exception as E:
                    print(f'{colorama.Fore.RED}{colorama.Style.BRIGHT}*{colorama.Style.RESET_ALL} %s' % (E))                 
             input('[ENTER}')
          else:
             if x == '2':
                while True:
                      data = http.joinTestSession(sessionName, sessionPass)                                     
                      try:
                         auth = data.headers['Set-Auth-Token']   
                         for student in data.json()['clientTestSessionDo']['studentSessionList']:
                             request = http.setReadyToConfirm(
                                       sessionPass,
                                       data.json()['clientTestSessionDo']['testSessionId'],
                                       student.get('assignedTest').get('testName') if student.get('assignedTest').get('testName') != None else config['manual_test_name'],
                                       student['studentId'],
                                       auth
                             )

                             print(f'{colorama.Style.BRIGHT}{colorama.Fore.GREEN}*{colorama.Style.RESET_ALL} s%s (%s)' % (student['userId'], request.text))
                      except Exception as E:
                         if data.headers.get('Set-Auth-Token') == None:
                            exit(print(f'{colorama.Style.BRIGHT}{colorama.Fore.RED}*{colorama.Style.RESET_ALL} Invalid Session'))
                         print(f'{colorama.Style.BRIGHT}{colorama.Fore.RED}*{colorama.Style.RESET_ALL} %s' % (E))
