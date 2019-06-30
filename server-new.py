import http.server
import socketserver
import termcolor
import requests

socketserver.TCPServer.allow_reuse_address = True

PORT = 8080


class TestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        print("GET received! Request line:")
        termcolor.cprint("  " + self.requestline, 'cyan')
        print("  Command: " + self.command)
        print("  Path: " + self.path)

        path = self.path

        if path == '/' or path == '/main_page.html' or path == '':
            f = open('main_page.html', 'r')
            main_contents = f.read()
            f.close()

            print(main_contents)
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(str.encode(main_contents)))
            self.end_headers()
            self.wfile.write(str.encode(main_contents))

        elif path.startswith('/listSpecies'):
            server = "http://rest.ensembl.org"
            ext = "/info/species?"
            r = requests.get(server + ext, headers={"Content-Type": "application/json"})

            data = r.json()
            species_list = data['species']

            ls_main = open('ls_main.html', 'r')
            ls_menu = ls_main.read()
            ls_main.close()

            ls_response = open('ls_response.html', 'r')
            ls_contents = ls_response.read()
            ls_response.close()

            if path == '/listSpecies' or path == '/listSpecies?limit=':
                for x in species_list:
                    ls_contents += '<p>' + x['name'] + '<p>'
                    ls_contents += '\r\n'
                self.send_response(200)


            elif path.startswith('/listSpecies?limit=') and path != '/listSpecies?limit=':
                limit = path.split('=')
                limit_num = limit[1]

                if not limit_num.isdigit():
                    f = open('ls_error.html', 'r')
                    ls_contents = f.read()
                    f.close()
                    self.send_response(404)



                else:
                    species_count = 0
                    for i in species_list:
                        ls_contents += '<p>' + i['name'] + '<p>'
                        ls_contents += '\r\n'
                        species_count += 1
                        if str(species_count) == limit[1]:
                            break
                    self.send_response(200)

            else:
                ls_contents = ls_menu
                self.send_response(200)

            f = open('main_return.html', 'r')
            end = f.read()
            f.close()
            ls_contents += end

            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(str.encode(ls_contents)))
            self.end_headers()
            self.wfile.write(str.encode(ls_contents))

        elif path.startswith('/karyotype'):

            kt_main = open('kt_main.html', 'r')
            kt_menu = kt_main.read()
            kt_main.close()

            kt_response = open('kt_response.html', 'r')
            kt_contents = kt_response.read()
            kt_response.close()

            if path == '/karyotype?specie=':
                f = open('kt_error.html', 'r')
                kt_contents = f.read()
                f.close()
                self.send_response(404)

            elif path.startswith('/karyotype?specie=') and path != '/karyotype?specie=':
                try:
                    species_r = path.split('=')
                    species_name = species_r[1]

                    server = "http://rest.ensembl.org"
                    ext = "/info/assembly/{}?".format(species_name)
                    r2 = requests.get(server + ext, headers={"Content-Type": "application/json"})

                    data2 = r2.json()

                    kt_contents += '<p>' + 'The karyotype for the species ' + str(species_name) + ' is: ' + '<p>'
                    for k in data2['karyotype']:
                        karyotype = str(k)
                        kt_contents += '<p>' + karyotype + '<p>'

                    self.send_response(200)

                except KeyError:
                    f = open('kt_error.html', 'r')
                    kt_contents = f.read()
                    f.close()
                    self.send_response(404)

            else:
                kt_contents = kt_menu
                self.send_response(200)

            f = open('main_return.html', 'r')
            end = f.read()
            f.close()
            kt_contents += end

            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(str.encode(kt_contents)))
            self.end_headers()
            self.wfile.write(str.encode(kt_contents))

        elif path.startswith('/chromosomeLength'):

            server = "http://rest.ensembl.org"
            ext = "/info/species?"
            r = requests.get(server + ext, headers={"Content-Type": "application/json"})

            data = r.json()
            species_info = data['species']
            name_list = []
            for x in species_info:
                name_list.append(x['name'])

            cl_main = open('cl_main.html', 'r')
            cl_menu = cl_main.read()
            cl_main.close()

            cl_response = open('cl_response.html', 'r')
            cl_contents = cl_response.read()
            cl_response.close()

            path = path.replace('&', ';')

            if path == '/chromosomeLength?specie=;chromo=':
                f = open('cl_error1.html', 'r')
                cl_contents = f.read()
                f.close()
                self.send_response(404)

            elif path.startswith('/chromosomeLength?specie='):
                try:
                    species_r = path.split('=')
                    species_r1 = species_r[1]
                    species_r2 = str(species_r1)
                    species_name = species_r2.split(';')[0]

                    server = "http://rest.ensembl.org"
                    ext = "/info/assembly/{}?".format(species_name)
                    r3 = requests.get(server + ext, headers={"Content-Type": "application/json"})

                    chromo_r = species_r[2]
                    chromo_chosen = str(chromo_r)

                    data3 = r3.json()

                    chromo_len = ''
                    for x in data3['top_level_region']:
                        if x['name'] == chromo_chosen:
                            chromo_len = x['length']
                            break

                    if chromo_len == '0' or chromo_len == '':
                        f = open('cl_error2.html', 'r')
                        cl_contents = f.read()
                        f.close()
                        self.send_response(404)

                    else:
                        cl_contents += '<p>' + 'The chromosome length for the chromosome ' + str(chromo_chosen)
                        cl_contents += ' of the species ' + str(species_name) + ' is: ' + str(chromo_len) + '<p>'
                        cl_contents += '\r\n'
                        self.send_response(200)
                except KeyError:
                    f = open('cl_error2.html', 'r')
                    cl_contents = f.read()
                    f.close()
                    self.send_response(404)

            else:
                cl_contents = cl_menu
                self.send_response(200)

            f = open('main_return.html', 'r')
            end = f.read()
            f.close()
            cl_contents += end

            print(cl_contents)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(str.encode(cl_contents)))
            self.end_headers()
            self.wfile.write(str.encode(cl_contents))

        else:
            f = open('main_error.html', 'r')
            error_msg = f.read()
            f.close()
            print(error_msg)
            self.send_response(404)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(str.encode(error_msg)))
            self.end_headers()
            self.wfile.write(str.encode(error_msg))


Handler = TestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("Serving at PORT", PORT)

    # -- Main loop: Attend the client. Whenever there is a new
    # -- clint, the handler is called
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Stopped by the user")
        httpd.server_close()
