#!/bin/env python3
# 
# compare package db between x86_64 and loong64
# borrowed table style from felixonmars@github

import pyalpm
import os
import sqlite3

DBS = ["core", "extra"]

common_header = '''
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://lib.baomitu.com/bulma/0.9.4/css/bulma.min.css">
<table class="table is-hoverable">'''

summary = common_header + '''
<thead><tr><th rowspan=2>Arch</th>
<th colspan=3>[core]</th><th colspan=3>[extra]</th>
<tr>
<th>Up-to-date (Ratio%)</th><th>Outdated</th><th>Missing</th>
<th>Up-to-date (Ratio%)</th><th>Outdated</th><th>Missing</th>
</tr></thead><tbody>'''

detail = common_header + '''
<thead><tr><th>package</th><th>x86_64</th><th>loong64</th><th>repo</th></tr></thead><tbody>
'''
pkgdata = {}
pkgrepo = {}
pkgcount = {}
conn = sqlite3.connect('packages.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# x86_64 as baseline
summary += "<tr><td>x86_64</td>"
handle = pyalpm.Handle("/", "/var/lib/pacman")
for repo in DBS:
    db_handle = handle.register_syncdb(repo, 0)
    pkgcount[repo] = 0
    for package in db_handle.search(""):
        pkgdata[package.name] = package.version
        pkgrepo[package.name] = repo
        pkgcount[repo] += 1
    summary += f"<td>{pkgcount[repo]}</td><td>0</td><td>0</td>"
summary += "</tr>"
conn.commit()

# loong64 as comparison
arch="loong64"
summary += f"<tr><td>{arch}</td>"
for repo in DBS:
    db_handle = handle.register_syncdb(f"{arch}-{repo}", 0)
    uptodate = 0
    outdated = 0
    for package in db_handle.search(""):
        if package.name in pkgdata:
            try:
                cursor.execute("insert into packages(name,loong_ver,x86_ver,repo,build_status) values (?,?,?,?,?)", (package.name, package.version, pkgdata[package.name], repo, "void"))
            except:
                pass
            version = package.version.split("-")
            version[1] = version[1].split(".")[0]
            version = "-".join(version)
            if pkgdata[package.name] == version:
                uptodate += 1
            else:
                detail += f"<tr><td>{package.name}</td><td>{pkgdata[package.name]}</td>"
                detail += f"<td>{package.version}</td><td>{repo}</td></tr>\n"
                outdated += 1
            del pkgdata[package.name]
        else:
            detail += f"<tr><td><font color=orange>{package.name}</td><td></td><td>"
            detail += f"{package.version}</td><td>{repo}</td></tr>\n"
            try:
                cursor.execute("insert into packages(name,loong_ver,x86_ver,repo,build_status) values (?,?,?,?,?)", (package.name, package.version, "missing", repo, "void"))
            except:
                pass
    percent = round((uptodate * 100.0 / pkgcount[repo]), 2)
    summary += f"<td><font color=green>{uptodate} ({percent}%)</font></td>"
    summary += f"<td><font color=orange>{outdated}</font></td>"
    summary += f"<td><font color=red>{pkgcount[repo] - uptodate - outdated}</font></td>"
summary += "</tr></tbody></table></div>"
conn.commit()
for pkg in pkgdata.keys():
    detail += f"<tr><td><font color=red>{pkg}</td><td>{pkgdata[pkg]}</td>"
    detail += f"<td><font color=red>missing</td><td>{pkgrepo[pkg]}</td></tr>\n"
    try:
        cursor.execute("insert into packages(name,loong_ver,x86_ver,repo,build_status) values (?,?,?,?,?)", (pkg, "missing", pkgdata[pkg], pkgrepo[pkg], "void"))
    except:
        pass
conn.commit()
detail += "</tbody></table></div>"
# Write the HTML content to a file
with open('summary.html', 'w') as f:
    f.write(summary)
with open('detail.html', 'w') as f:
    f.write(detail)
