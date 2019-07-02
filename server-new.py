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

        f = open('main_return.html', 'r')
        end = f.read()
        f.close()
        path = self.path

        if path == '/' or path == '/main_page.html' or path == '':
            f = open('main_page.html', 'r')
            main_contents = f.read()
            f.close()

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

            cl_contents += end
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(str.encode(cl_contents)))
            self.end_headers()
            self.wfile.write(str.encode(cl_contents))

        elif path.startswith('/geneSeq'):
            gs_main = open('gs_main.html', 'r')
            gs_menu = gs_main.read()
            gs_main.close()

            gs_response = open('gs_response.html', 'r')
            gs_contents = gs_response.read()
            gs_response.close()

            if path == '/geneSeq?gene=':
                gs_error1 = open('gs_error1.html', 'r')
                gs_contents = gs_error1.read()
                gs_error1.close()
                self.send_response(404)

            elif path.startswith('/geneSeq?gene='):
                gene_r = path.split('=')
                gene_chosen = gene_r[1]

                server = "http://rest.ensembl.org"
                ext = "/lookup/symbol/homo_sapiens/{}?".format(gene_chosen)
                r4 = requests.get(server + ext, headers={"Content-Type": "application/json"})
                data4 = r4.json()

                try:
                    seq_id = data4['id']
                    server = "http://rest.ensembl.org"
                    ext = "/sequence/id/{}?".format(seq_id)
                    r4_1 = requests.get(server + ext, headers={"Content-Type": "application/json"})
                    data4_1 = r4_1.json()

                    seq = data4_1['seq']
                    gs_contents += '<p>' + 'The sequence of the gene ' + str(gene_chosen) + ' is: '
                    gs_contents += str(seq) + '<p>'
                    self.send_response(200)

                except KeyError:
                    gs_error2 = open('gs_error2.html', 'r')
                    gs_contents = gs_error2.read()
                    gs_error2.close()
                    self.send_response(404)

            else:
                gs_contents = gs_menu
                self.send_response(200)

            gs_contents += end
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(str.encode(gs_contents)))
            self.end_headers()
            self.wfile.write(str.encode(gs_contents))

        elif path.startswith('/geneInfo'):
            gi_main = open('gi_main.html', 'r')
            gi_menu = gi_main.read()
            gi_main.close()

            gi_response = open('gi_response.html', 'r')
            gi_contents = gi_response.read()
            gi_response.close()

            if path == '/geneInfo?gene=':
                gs_error1 = open('gs_error1.html', 'r')
                gi_contents = gs_error1.read()
                gs_error1.close()
                self.send_response(404)

            elif path.startswith('/geneInfo?gene='):

                gene_r = path.split('=')
                gene_chosen = gene_r[1]

                server = "http://rest.ensembl.org"
                ext = "/lookup/symbol/homo_sapiens/{}?".format(gene_chosen)
                r4 = requests.get(server + ext, headers={"Content-Type": "application/json"})
                data4 = r4.json()

                server = "http://rest.ensembl.org"
                ext = "/lookup/symbol/homo_sapiens/{}?".format(gene_chosen)
                r5 = requests.get(server + ext, headers={"Content-Type": "application/json"})
                data5 = r5.json()

                try:
                    seq_id = data4['id']
                    server = "http://rest.ensembl.org"
                    ext = "/sequence/id/{}?".format(seq_id)
                    r4_1 = requests.get(server + ext, headers={"Content-Type": "application/json"})
                    data4_1 = r4_1.json()

                    seq = data4_1['seq']
                    gene_length = len(seq)

                    seq_id = data5['id']

                    server = "http://rest.ensembl.org"
                    ext = "/lookup/id/{}?".format(seq_id)
                    r5_1 = requests.get(server + ext, headers={"Content-Type": "application/json"})

                    data5_1 = r5_1.json()
                    gene_start = data5_1['start']
                    gene_end = data5_1['end']
                    gene_id = data5_1['id']
                    gene_chromo = data5_1['seq_region_name']

                    gi_contents += '<p>' + '          Start: ' + str(gene_start) + '<p>' + '\r\n'
                    gi_contents += '<p>' + '            End: ' + str(gene_end) + '<p>' + '\r\n'
                    gi_contents += '<p>' + '             ID: ' + str(gene_id) + '<p>' + '\r\n'
                    gi_contents += '<p>' + '         Length: ' + str(gene_length) + '<p>' + '\r\n'
                    gi_contents += '<p>' + '     Chromosome: ' + str(gene_chromo) + '<p>' + '\r\n'
                    self.send_response(200)

                except KeyError:
                    gs_error2 = open('gs_error2.html', 'r')
                    gi_contents = gs_error2.read()
                    gs_error2.close()
                    self.send_response(404)

            else:
                gi_contents = gi_menu
                self.send_response(200)

            gi_contents += end

            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(str.encode(gi_contents)))
            self.end_headers()
            self.wfile.write(str.encode(gi_contents))

        elif path.startswith('/geneCalc'):
            gc_main = open('gc_main.html', 'r')
            gc_menu = gc_main.read()
            gc_main.close()

            gc_response = open('gc_response.html', 'r')
            gc_contents = gc_response.read()
            gc_response.close()

            if path == '/geneCalc?gene=':
                gs_error1 = open('gs_error1.html', 'r')
                gc_contents = gs_error1.read()
                gs_error1.close()

            elif path.startswith('/geneCalc?gene='):

                gene_r = path.split('=')
                gene_chosen = gene_r[1]

                server = "http://rest.ensembl.org"
                ext = "/lookup/symbol/homo_sapiens/{}?".format(gene_chosen)
                r6 = requests.get(server + ext, headers={"Content-Type": "application/json"})
                data6 = r6.json()

                try:
                    seq_id = data6['id']
                    server = "http://rest.ensembl.org"
                    ext = "/sequence/id/{}?".format(seq_id)
                    r6_1 = requests.get(server + ext, headers={"Content-Type": "application/json"})
                    data6_1 = r6_1.json()

                    seq = data6_1['seq']
                    seq_length = len(seq)
                    a_count = 0
                    g_count = 0
                    c_count = 0
                    t_count = 0
                    for x in range(len(seq)):
                        if seq[x] == "A":
                            a_count += 1
                        elif seq[x] == "G":
                            g_count += 1
                        elif seq[x] == "C":
                            c_count += 1
                        elif seq[x] == "T":
                            t_count += 1
                    a_perc = round(100 * (a_count / seq_length))
                    g_perc = round(100 * (g_count / seq_length))
                    c_perc = round(100 * (c_count / seq_length))
                    t_perc = round(100 * (t_count / seq_length))

                    gc_contents += '<p>' + 'Length: ' + str(seq_length) + ' bases' + '<p>' + '\r\n'
                    gc_contents += '<p>' + 'Number of bases: '
                    gc_contents += 'A: {}  G: {}  C: {}  T: {} '.format(a_count, g_count, c_count, t_count) + '<p>'
                    gc_contents += '\r\n' + '<p>' + 'Percentages of bases: '
                    gc_contents += 'A: {}%  G: {}%  C: {}%  T: {}% '.format(a_perc, g_perc, c_perc, t_perc) + '<p>'
                    self.send_response(200)

                except KeyError:
                    gs_error2 = open('gs_error2.html', 'r')
                    gc_contents = gs_error2.read()
                    gs_error2.close()
                    self.send_response(404)

            else:
                gc_contents = gc_menu
                self.send_response(200)

            gc_contents += end

            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(str.encode(gc_contents)))
            self.end_headers()
            self.wfile.write(str.encode(gc_contents))

        elif path.startswith('/geneList'):
            gl_main = open('gl_main.html', 'r')
            gl_menu = gl_main.read()
            gl_main.close()

            gl_response = open('gl_response.html', 'r')
            gl_contents = gl_response.read()
            gl_response.close()

            path = path.replace('&', ';')
            if path.startswith('/geneList?chromo=;'):
                gl_error1 = open('gl_error1.html', 'r')
                gl_contents = gl_error1.read()
                gl_error1.close()
                self.send_response(404)

            elif path.startswith('/geneList?chromo='):
                path_r = path.split('?')
                path_r1 = str(path_r).split('=')
                try:
                    path_r21 = path_r1[1]
                    path_r22 = path_r1[2]
                    path_r33 = path_r1[3]

                    path_r31 = path_r21.split(';')
                    chromo = path_r31[0]

                    path_r32 = path_r22.split(';')
                    chromo_start = path_r32[0]

                    chromo_end = path_r33.split('\'')[0]

                    server = "http://rest.ensembl.org"
                    ext_r = "/overlap/region/human/{}:{}-{}?".format(chromo, chromo_start, chromo_end)
                    ext = ext_r + "feature=gene;feature=transcript;feature=cds;feature=exon"
                    r = requests.get(server + ext, headers={"Content-Type": "application/json"})
                    data7 = r.json()

                    gl_contents += '<p>' + 'In the chromosome ' + str(chromo) + ' and between'
                    gl_contents += ' {} and {}'.format(chromo_start, chromo_end) + ' we find:' + '<p>\r\n'
                    count = 0
                    for x in data7:
                        ft_type = x['feature_type']
                        if ft_type == 'gene':
                            ext_name = x['external_name']
                            gl_contents += '<p>' + ext_name + '<p>\r\n'
                            count += 1
                    gl_contents += '<p>' + 'There are a total of {} genes in between'.format(count) + '<p>'
                    self.send_response(200)

                except TypeError:
                    gl_error2 = open('gl_error2.html', 'r')
                    gl_contents = gl_error2.read()
                    gl_error2.close()
                    self.send_response(404)

            else:
                gl_contents = gl_menu
                self.send_response(200)

            gl_contents += end
            print(gl_contents)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(str.encode(gl_contents)))
            self.end_headers()
            self.wfile.write(str.encode(gl_contents))

        else:
            f = open('main_error.html', 'r')
            error_msg = f.read()
            f.close()
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
