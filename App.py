from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

conn = cursor = None

def openDb():
    global conn, cursor
    conn = sqlite3.connect('nilai_mahasiswa.db')
    cursor = conn.cursor()

def closeDb():
    global conn, cursor
    cursor.close()
    conn.close()

def inisialisasi_db():
    openDb()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS mahasiswa (
        nim TEXT PRIMARY KEY,
        nama TEXT,
        program_studi TEXT,
        kelas TEXT,
        presensi INTEGER,
        tugas INTEGER,
        uts INTEGER,
        uas INTEGER,
        total_nilai REAL,
        rata_rata_nilai REAL,
        nilai_huruf TEXT,
        status TEXT
    )
    ''')
    conn.commit()
    closeDb()

def hitung_nilai_presensi(presensi):
    return 100 if presensi == 16 else (presensi / 16.0) * 100

def hitung_total_nilai(presensi, tugas, uts, uas):
    total_nilai = hitung_nilai_presensi(presensi) + tugas + uts + uas
    return round(total_nilai, 2)

def hitung_rata_rata_nilai(total_nilai):
    rata_rata_nilai = total_nilai / 4
    return round(rata_rata_nilai, 2)

def hitung_nilai_huruf(rata_rata_nilai):
    if rata_rata_nilai >= 80:
        return 'A'
    elif rata_rata_nilai >= 70:
        return 'B'
    elif rata_rata_nilai >= 60:
        return 'C'
    elif rata_rata_nilai >= 50:
        return 'D'
    else:
        return 'E'

def tentukan_status(nilai_huruf):
    return 'Lulus' if nilai_huruf in ['A', 'B', 'C'] else 'Tidak Lulus'

@app.route('/')
def index():
    openDb()
    container = []
    for row in cursor.execute('SELECT nim, nama, program_studi, kelas, rata_rata_nilai, nilai_huruf, status FROM mahasiswa'):
        container.append(row)
    closeDb()
    return render_template('Beranda.html', container=container)

@app.route('/detail/<nim>')
def detail(nim):
    openDb()
    cursor.execute('SELECT * FROM mahasiswa WHERE nim = ?', (nim,))
    data = cursor.fetchone()
    closeDb()
    return render_template('detail.html', data=data)

@app.route('/tambah', methods=['GET', 'POST'])
def tambah():
    if request.method == 'POST':
        nim = request.form['nim']
        nama = request.form['nama']
        program_studi = request.form['program_studi']
        kelas = request.form['kelas']
        presensi = int(request.form['presensi'])
        tugas = int(request.form['tugas'])
        uts = int(request.form['uts'])
        uas = int(request.form['uas'])

        total_nilai = hitung_total_nilai(presensi, tugas, uts, uas)
        rata_rata_nilai = hitung_rata_rata_nilai(total_nilai)
        nilai_huruf = hitung_nilai_huruf(rata_rata_nilai)
        status = tentukan_status(nilai_huruf)

        openDb()
        cursor.execute('''
            INSERT INTO mahasiswa (nim, nama, program_studi, kelas, presensi, tugas, uts, uas, total_nilai, rata_rata_nilai, nilai_huruf, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (nim, nama, program_studi, kelas, presensi, tugas, uts, uas, total_nilai, rata_rata_nilai, nilai_huruf, status))
        conn.commit()
        closeDb()
        return redirect(url_for('index'))
    return render_template('tambah.html')

@app.route('/edit/<nim>', methods=['GET', 'POST'])
def edit(nim):
    openDb()
    cursor.execute('SELECT * FROM mahasiswa WHERE nim = ?', (nim,))
    data = cursor.fetchone()

    if request.method == 'POST':
        nama = request.form['nama']
        program_studi = request.form['program_studi']
        kelas = request.form['kelas']
        presensi = int(request.form['presensi'])
        tugas = int(request.form['tugas'])
        uts = int(request.form['uts'])
        uas = int(request.form['uas'])

        total_nilai = hitung_total_nilai(presensi, tugas, uts, uas)
        rata_rata_nilai = hitung_rata_rata_nilai(total_nilai)
        nilai_huruf = hitung_nilai_huruf(rata_rata_nilai)
        status = tentukan_status(nilai_huruf)

        cursor.execute('''
            UPDATE mahasiswa SET nama=?, program_studi=?, kelas=?, presensi=?, tugas=?, uts=?, uas=?, total_nilai=?, rata_rata_nilai=?, nilai_huruf=?, status=?
            WHERE nim=?''', 
            (nama, program_studi, kelas, presensi, tugas, uts, uas, total_nilai, rata_rata_nilai, nilai_huruf, status, nim))
        conn.commit()
        closeDb()
        return redirect(url_for('index'))
    closeDb()
    return render_template('update.html', data=data)

@app.route('/hapus/<nim>', methods=['GET', 'POST'])
def hapus(nim):
    openDb()
    cursor.execute('DELETE FROM mahasiswa WHERE nim=?', (nim,))
    conn.commit()
    closeDb()
    return redirect(url_for('index'))

if __name__ == '__main__':
    inisialisasi_db()
    app.run(host='0.0.0.0', port=5000)
