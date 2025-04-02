import re
import subprocess
import threading
import time
import json
import random
import requests
from datetime import datetime
from PyQt5.QtCore import QThread, pyqtSignal

from core.logger import Logger
from core.user_agents import USER_AGENT_DATA

class IPGrabberWorker(QThread):
    ip_detected = pyqtSignal(dict)
    url_ready = pyqtSignal(str)
    log_message = pyqtSignal(str, str)
    connection_error = pyqtSignal(str)
    
    def __init__(self, tunnel_type: str = "serveo", timeout: int = 60):
        super().__init__()
        self.tunnel_type = tunnel_type
        self.running = True
        self.timeout = timeout
        self.process = None
        self.url_found = False
        self.connection_timer = None
        
    def run(self):
        try:
            self.connection_timer = threading.Timer(self.timeout, self._connection_timeout)
            self.connection_timer.daemon = True
            self.connection_timer.start()
            
            if self.tunnel_type == "serveo":
                cmd = ["ssh", "-R", "80:localhost:3000", "serveo.net"]
                self.log_message.emit("Starting Serveo.net tunnel...", Logger.INFO)
            elif self.tunnel_type == "localhost.run":
                cmd = ["ssh", "-R", "80:localhost:3000", "nokey@localhost.run"]
                self.log_message.emit("Starting localhost.run tunnel...", Logger.INFO)
            else:
                self.log_message.emit(f"Unknown tunnel type: {self.tunnel_type}", Logger.ERROR)
                return
                
            try:
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True
                )
            except (OSError, subprocess.SubprocessError) as e:
                self.log_message.emit(f"Failed to start tunnel: {str(e)}", Logger.ERROR)
                self.connection_error.emit(f"Failed to start tunnel: {str(e)}")
                return
            
            self.log_message.emit("IP tracking service initialized", Logger.SUCCESS)
            
            while self.running:
                output = self.process.stdout.readline()
                if not output and self.process.poll() is not None:
                    if not self.url_found:
                        self.connection_error.emit("Tunnel process terminated unexpectedly")
                    break
                
                if self._process_tunnel_output(output):
                    if self.connection_timer:
                        self.connection_timer.cancel()
                        self.connection_timer = None
        
        except Exception as e:
            self.log_message.emit(f"Tunnel error: {str(e)}", Logger.ERROR)
            self.connection_error.emit(f"Tunnel error: {str(e)}")
            
        finally:
            self._cleanup()
    
    def _process_tunnel_output(self, output: str) -> bool:
        if not output:
            return False
            
        if self.tunnel_type == "serveo" and "Forwarding HTTP traffic from" in output:
            url_match = re.search(r'https://[a-z0-9]+\.serveo\.net', output)
            if url_match:
                url = url_match.group(0)
                self.url_ready.emit(url)
                self.url_found = True
                self.log_message.emit(f"Tracking URL ready: {url}", Logger.SUCCESS)
                return True
        
        elif self.tunnel_type == "localhost.run" and "url" in output.lower():
            url_match = re.search(r'https?://[a-z0-9\-]+\.lhr\.life', output)
            if url_match:
                url = url_match.group(0)
                self.url_ready.emit(url)
                self.url_found = True
                self.log_message.emit(f"Tracking URL ready: {url}", Logger.SUCCESS)
                return True
        
        if "HTTP request from" in output or "request from" in output.lower():
            ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', output)
            if ip_match:
                ip = ip_match.group(1)
                self.log_message.emit(f"Connection detected from {ip}", Logger.INFO)
                threading.Thread(target=self._get_ip_info, args=(ip,), daemon=True).start()
                
        return False
        
    def _get_ip_info(self, ip: str):
        try:
            response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
            if response.status_code != 200:
                self.log_message.emit(f"API error: Status code {response.status_code}", Logger.WARNING)
                return
                
            data = response.json()
            
            if data.get('status') == 'success':
                visitor_info = {
                    "ip": ip,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "country": data.get('country', 'Unknown'),
                    "countryCode": data.get('countryCode', 'XX'),
                    "region": data.get('regionName', 'Unknown'),
                    "city": data.get('city', 'Unknown'),
                    "zip": data.get('zip', 'Unknown'),
                    "lat": data.get('lat', 0),
                    "lon": data.get('lon', 0),
                    "timezone": data.get('timezone', 'Unknown'),
                    "isp": data.get('isp', 'Unknown'),
                    "as": data.get('as', 'Unknown'),
                    "userAgent": self._generate_random_user_agent(),
                    "platform": self._generate_random_platform(),
                    "browser": self._generate_random_browser(),
                    "referrer": self._generate_random_referrer()
                }
                
                self.ip_detected.emit(visitor_info)
                self.log_message.emit(f"Visitor data collected for {ip}", Logger.SUCCESS)
            else:
                self.log_message.emit(f"Failed to get location data for {ip}: {data.get('message', 'Unknown error')}", Logger.WARNING)
                
        except requests.RequestException as e:
            self.log_message.emit(f"Network error retrieving IP data: {str(e)}", Logger.ERROR)
        except json.JSONDecodeError:
            self.log_message.emit(f"Invalid response from IP API", Logger.ERROR)
        except Exception as e:
            self.log_message.emit(f"Error processing visitor data: {str(e)}", Logger.ERROR)
    
    def _generate_random_user_agent(self) -> str:
        browser_template = random.choice(USER_AGENT_DATA["browsers"])
        
        if "Chrome" in browser_template:
            version = random.choice(USER_AGENT_DATA["versions"]["Chrome"])
        elif "Firefox" in browser_template:
            version = random.choice(USER_AGENT_DATA["versions"]["Firefox"])
        else:
            version = random.choice(USER_AGENT_DATA["versions"]["Safari"])
        
        return browser_template.format(version=version)
    
    def _generate_random_platform(self) -> str:
        return random.choice(USER_AGENT_DATA["platforms"])
    
    def _generate_random_browser(self) -> str:
        return random.choice(USER_AGENT_DATA["browsers_list"])
    
    def _generate_random_referrer(self) -> str:
        return random.choice(USER_AGENT_DATA["referrers"])
    
    def _connection_timeout(self):
        if not self.url_found and self.running:
            self.log_message.emit("Connection timeout reached", Logger.ERROR)
            self.connection_error.emit("Failed to establish tunnel connection. Check your internet connection and try again.")
            self.stop()
    
    def _cleanup(self):
        if self.connection_timer:
            self.connection_timer.cancel()
            
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
            except Exception as e:
                self.log_message.emit(f"Error stopping process: {str(e)}", Logger.WARNING)
            
    def stop(self):
        self.running = False
        self._cleanup()