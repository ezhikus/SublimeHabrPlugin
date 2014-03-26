import sublime, sublime_plugin
import json
import urllib
import SublimeHabrPlugin.websocket
import sys

def download_url_to_string(url):
	request = urllib.request.Request(url)
	response = urllib.request.urlopen(request)
	html = response.read()
	return html

def send_to_socket(socket, data):
	socket.send(data)

def send_script_to_socket(socket, script):
	send_to_socket(socket, '{"id": 1, "method": "Runtime.evaluate", "params": { "expression": "' + script + '", "returnByValue": false}}')

def on_open(ws):
	print('Websocket open, text:' + ws.text)
	send_script_to_socket(ws, 'document.getElementById(\'text_textarea\').innerHTML = \'' + ws.text + '\';document.getElementsByName(\'preview\')[0].click();')

def on_message(ws, message):
	decoded_message = json.loads(message)
	print(decoded_message)
	ws.close()

def connect_to_websocket(url):
	res = SublimeHabrPlugin.websocket.WebSocketApp(url, on_message = on_message)
	res.on_open = on_open
	return res

class HabrCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		text = self.view.substr(sublime.Region(0, self.view.size()))
		info_about_tabs = download_url_to_string('http://localhost:9222/json')
		info_about_tabs = info_about_tabs.decode("utf-8")
		decoded_data = json.loads(info_about_tabs)
		first_tab_websocket_url = decoded_data[0]['webSocketDebuggerUrl']
		print(first_tab_websocket_url)
		first_tab_websocket = connect_to_websocket(first_tab_websocket_url)
		first_tab_websocket.text = text
		first_tab_websocket.run_forever()
