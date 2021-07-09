import sys, os, socket, datetime, argparse, webbrowser

class HTTPServer:
    def __init__(self, port, auth="default"):
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("127.0.0.1", port))
        self.server_socket.listen()

        self.delete_auth = auth

        self.type_dict = {
            "html" : "text/html; charset=utf-8",
            "txt"  : "text/html; charset=utf-8",
            "pdf"  : "application/pdf",
            ""     : "text/html; charset=utf-8",
            "jpg"  : "image/jpeg",
            "ico"  : "image/x-icon",
            "js"   : "text/javascript; charset=utf-8",
            "css"  : "text/css",
        }

        self.status_codes = {
            "100" : "Continue",
            "101" : "Switching Protocols",
            "102" : "Processing",

            "200" : "OK",
            "201" : "Created",
            "202" : "Accepted",
            "203" : "Non-authoritative Information",
            "204" : "No Content",
            "205" : "Reset Content",
            "206" : "Partial Content",
            "207" : "Multi-Status",
            "208" : "Already Reported",
            "226" : "IM Used",
            
            "300" : "Multiple Choices",
            "301" : "Moved Permanently",
            "302" : "Found",
            "303" : "See Other",
            "304" : "Not Modified",
            "305" : "Use Proxy",
            "307" : "Temporary Redirect",
            "308" : "Permanent Redirect",
            
            "400" : "Bad Request",
            "401" : "Unauthorized",
            "402" : "Payment Required",
            "403" : "Forbidden",
            "404" : "Not Found",
            "405" : "Method Not Allowed",
            "406" : "Not Acceptable",
            "407" : "Proxy Authentication Required",
            "408" : "Request Timeout",
            "409" : "Conflict",
            "410" : "Gone",
            "411" : "Length Required",
            "412" : "Precondition Failed",
            "413" : "Payload Too Large",
            "414" : "Request-URI Too Long",
            "415" : "Unsupported Media Type",
            "416" : "Requested Range Not Satisfiable",
            "417" : "Expectation Failed",
            "418" : "I'm a teapot",
            "421" : "Misdirected Request",
            "422" : "Unprocessable Entity",
            "423" : "Locked",
            "424" : "Faild Dependency",
            "426" : "Upgrade Required",
            "428" : "Precondition Required",
            "429" : "Too Many Requests",
            "431" : "Request Header Fields Too Large",
            "444" : "Connection Closed Without Response",
            "451" : "Unavailable For Legeal Reasons",
            "499" : "Client CLosed Request",

            "500" : "Internal Server Error",
            "501" : "Not Implemented",
            "502" : "Bad Gateway",
            "503" : "Service Unavailable",
            "504" : "Gateway Timeout",
            "505" : "HTTP Version Not Supported",
            "506" : "Varient Also Negotiates",
            "507" : "Insufficient Storage",
            "508" : "Loop Detected",
            "510" : "Not Extended",
            "511" : "Network Authentication Required",
            "599" : "Network Connection Timeout Error",
        }

    def send_headers(self, headers):
        """Join a header list, decode, and send it to client."""
        headers = " ".join(headers) + "\r\n"
        print(headers)
        self.client_socket.send(headers.encode())

    def parse_request(self, request):
        """Parse request from client to dict of field-value."""
        request = request.split("\r\n")
        parsed = dict()
        parsed["basic_info"] = request[0].split()

        for i, line in enumerate(request, 1):
            if ":" in line[:line.find(" ")]:
                line = line.split(": ")
                key = line[0]
                value = ": ".join(line[1:])
                parsed[key] = value
            else:
                parsed["payload"] = "\r\n".join(request[i:])
        return parsed

    def send_GET_headers(self, data):
        """Respond to GET."""
        file_name = data["basic_info"][1]
        if os.path.isfile(file_name):
            code = "200"
        
            file = open(file_name, "rb")
            file_data = file.read()
            file.close()

            if "." in file_name[file_name.rfind("/"):]:
                file_extension = file_name.split(".")[-1]
            else:
                file_extension = ""
            
            if file_extension not in self.type_dict:
                file_extension = ""

            headers = ["HTTP/1.1", code, self.status_codes[code] + "\r\n", "Content-Length:", str(len(file_data)) + "\r\n", "Content-Type:", self.type_dict[file_extension] + "\r\n"]
            

            self.send_headers(headers)

        else:
            code = "404"
            headers = ["HTTP/1.1", code, self.status_codes[code]]
            self.send_headers(headers)
        return code


    def GET(self, data):
        """GET handaling"""
        print(data["basic_info"][1])

        if data["basic_info"][1] == "/":
            data["basic_info"][1] = "./index.html"

        elif os.path.isfile("." + data["basic_info"][1]):
            data["basic_info"][1] = "." + data["basic_info"][1]
        else:
            data["basic_info"][1] = "./404.html"
        

        code = self.send_GET_headers(data)

        if code == "200":

            file = open(data["basic_info"][1], "rb")
            file_data = file.read()
            file.close()

            self.client_socket.send(file_data)
        
        return code

    def HEAD(self, data):
        """HEAD handaling"""
        print(data["basic_info"][1])

        if data["basic_info"][1] == "/":
            data["basic_info"][1] = "index.html"
        elif os.path.isfile("." + data["basic_info"][1]):
            data["basic_info"][1] = "." + data["basic_info"][1]
        else:
            data["basic_info"][1] = "./404.html"

        return self.send_GET_headers(data)


    def DELETE(self, data):
        """DELETE handaling"""
        file = "." + data["basic_info"][1]
        
        auth = ""
        if "Authorization" in data:
            auth = data["Authorization"]

        if os.path.isfile(file) and (auth == self.delete_auth or self.delete_auth == "None"):
            code = "200"

            os.remove(file)


            payload = '{"success":"true"}'

            headers = ["HTTP/1.1", code, self.status_codes[code] + "\r\n", "Content-Length:", str(len(payload)) + "\r\n", "Content-Type: application/json\r\n", payload + "\r\n"]
            self.send_headers(headers)

            return code
        
        elif auth != self.delete_auth and self.delete_auth != "None":
            code = "401"
        else:
            code = "404"

        headers = ["HTTP/1.1", code, self.status_codes[code] + "\r\n"]
        self.send_headers(headers)
        
        return code


    def OPTIONS(self, data):
        """OPTIONS handaling"""
        code = "204"
        time = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
        headers = ["HTTP/1.1", code, self.status_codes[code] + "\r\n", "Allow: OPTIONS, GET, HEAD, DELETE\r\n", "Date:", time + "\r\n", f"Server: Python/{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}\r\n"]
        headers = " ".join(headers) + "\r\n"

        self.client_socket.send(headers.encode())
        return code

    def recv(self):
        """Read request until it's end."""
        data = ""
        new_data = "0" * 1024

        self.client_socket, _ = self.server_socket.accept()
        while len(new_data) == 1024:
            new_data = self.client_socket.recv(1024).decode()
            data += new_data
        
        return data

    def start(self):
        """Start the server."""
        print("Server running.")
        while True:
            try:
                data = self.recv()
                data = self.parse_request(data)

                if len(data) > 0:
                    if data["basic_info"][1].startswith("/.git"):
                        webbrowser.open("https://www.youtube.com/watch?v=oHg5SJYRHA0", new=0, autoraise=True)
                        data["basic_info"][1] = "this_file_does_not_exist.you_just_got_rickrolled"
                    
                    if data["basic_info"][0] == "GET":
                        self.GET(data)
                    elif data["basic_info"][0] == "HEAD":
                        self.HEAD(data)
                    elif data["basic_info"][0] == "DELETE":
                        self.DELETE(data)
                    elif data["basic_info"][0] == "OPTIONS":
                        self.OPTIONS(data)
                
                self.client_socket.close()
            
            except KeyboardInterrupt:
                self.server_socket.close()
                print("Server closed.")
                break
            
            except Exception as e:
                print(e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", default=80, help="Port for the server.")
    parser.add_argument("-a", "--auth", default="default", help='Auth key for file deleting, use None to allow deleing without key.')

    args = parser.parse_args()

    http_server = HTTPServer(args.port, args.auth)
    http_server.start()