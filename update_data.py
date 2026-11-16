#!/usr/bin/env python3
"""Buat data.js untuk dashboard dari file DBF SHP (zona) dan POIN (titik) Pangandaran.

Cara pakai:
  1. Taruh file .dbf SHP dan POIN terbaru di folder data_mentah/ (hapus yang lama).
  2. Jalankan:  python update_data.py
  3. Upload data.js yang baru ke GitHub / Netlify.

Tidak butuh library tambahan, hanya Python 3.
Nama surveyor untuk zona yang kolom Surveyor-nya kosong atau "-" diambil dari surveyor_zona.csv.
"""
import json, struct, glob, os, csv, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))

def read_dbf(path):
    b = open(path, 'rb').read()
    n, hl, rl = struct.unpack('<IHH', b[4:12])
    fields, o = [], 32
    while b[o] != 0x0D:
        fields.append((b[o:o+11].split(b'\0')[0].decode('latin1'), chr(b[o+11]), b[o+16])); o += 32
    rows = []
    for i in range(n):
        p = hl + i * rl
        if b[p] == 0x2A: continue
        p += 1; r = {}
        for name, t, ln in fields:
            s = b[p:p+ln].decode('latin1').strip(); p += ln
            if t in 'NF':
                try: r[name] = float(s) if s else None
                except ValueError: r[name] = None
            else: r[name] = s
        rows.append(r)
    return [f[0] for f in fields], rows

def ok_kab(r):
    k = str(r.get('WADMKK') or '')
    return (not k) or 'pangandaran' in k.lower()

def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'data_mentah')
    zones, points, files = [], [], []
    for path in sorted(glob.glob(os.path.join(folder, '*.dbf')) + glob.glob(os.path.join(folder, '*.DBF'))):
        names, rows = read_dbf(path); base = os.path.basename(path)
        if 'Nomor_Samp' in names and 'Tanggal_Pe' in names:
            kind = 'POIN'
            for r in rows:
                if not ok_kab(r): continue
                no = r.get('Nomor_Samp')
                points.append({'no': None if no is None else round(no), 'svy': r.get('Nama_Surve') or '',
                    'tp': r.get('Tanggal_Pe') or '', 'tt': r.get('Tanggal__1') or '', 'jenis': r.get('Jenis_Data') or '',
                    'zona': r.get('HISTZONE') or '', 'nilai': r.get('Nilai_Ta_1') or 0, 'kec': (r.get('Kecamatan') or '').replace('Kecamatan ', '').strip(), 'desa': (r.get('Kelurahan') or '').strip(),
                    'luasT': r.get('Luas_tanah') or 0, 'jalan': r.get('Kelas_Jala') or '', 'akses': r.get('Aksesibili') or '', 'jns': r.get('Jenis') or '',
                    'x': r.get('X') or 0, 'y': r.get('Y') or 0})
        elif 'HISTZONE' in names:
            kind = 'SHP'
            for r in rows:
                if not ok_kab(r): continue
                zones.append({'zona': r.get('HISTZONE') or '', 'guna': r.get('PENGGUNAAN') or '',
                    'luas': r.get('Luas_M2') or r.get('Shape_Area') or 0,
                    'n': r.get('Jml_Titik') if 'Jml_Titik' in names else None,
                    'rsd': r.get('RSD_Persen') if 'RSD_Persen' in names else None,
                    'rata': r.get('Rata_Nilai') if 'Rata_Nilai' in names else None,
                    'svy': r.get('Surveyor') or ''})
        else:
            print('Dilewati (bukan SHP/POIN):', base); continue
        files.append({'name': base, 'type': kind, 'rows': len(rows)})
        print(f'{base}: {kind}, {len(rows)} baris')
    if not zones or not points:
        sys.exit('Butuh sedikitnya satu file SHP (zona) dan satu file POIN (titik) di folder ' + folder)
    # samakan ejaan nama surveyor di SHP dengan nama di titik (mis. "Rafid Rahmad" -> "Rafid Rahmat")
    import difflib
    kanon = sorted({p['svy'] for p in points if p['svy']})
    def canon(n):
        if not n or n == '-' or n in kanon: return n
        m = difflib.get_close_matches(n, kanon, n=1, cutoff=0.8)
        return m[0] if m else n
    for z in zones: z['svy'] = canon(z['svy'])
    svymap = {}
    p = os.path.join(HERE, 'surveyor_zona.csv')
    if os.path.exists(p):
        for row in csv.DictReader(open(p, encoding='utf-8')):
            svymap[row['HISTZONE']] = canon(row['SVY_FIX'])
    data = {'updated': datetime.datetime.now().strftime('%d-%m-%Y %H:%M'), 'zones': zones, 'points': points,
            'files': files, 'svymap': svymap}
    with open(os.path.join(HERE, 'data.js'), 'w', encoding='utf-8') as f:
        f.write('window.DATA=' + json.dumps(data, separators=(',', ':')) + ';\n')
    print(f'Selesai: {len(zones)} zona, {len(points)} titik -> data.js')

main()
