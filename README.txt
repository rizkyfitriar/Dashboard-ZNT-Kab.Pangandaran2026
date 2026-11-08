DASHBOARD ZNT KAB. PANGANDARAN 2026

Isi folder
  index.html        halaman dashboard
  data.js           data yang ditampilkan (dibuat oleh update_data.py)
  zona_geo.js       bentuk zona untuk peta (tetap, kecuali zona diubah)
  surveyor_zona.csv daftar surveyor per zona (dipakai bila kolom Surveyor di SHP kosong atau "-")
  update_data.py    skrip pembuat data.js
  leaflet/          pustaka peta (jangan dihapus)
  data_mentah/      taruh DBF SHP dan POIN terbaru di sini

UPDATE DATA (setiap ada data baru)
  1. Export / salin file .dbf SHP (zona) dan POIN (titik) dari ArcGIS.
  2. Hapus DBF lama di data_mentah/, taruh DBF baru (satu SHP, satu POIN).
  3. Jalankan:  python update_data.py
  4. Upload ulang data.js ke GitHub / Netlify. Link yang sama langsung menampilkan data terbaru.

PUBLISH PERTAMA KALI
  Netlify Drop : buka app.netlify.com/drop, seret seluruh folder ini (tanpa data_mentah bila tidak ingin file mentah terbuka).
  GitHub Pages : upload isi folder ke repository publik, Settings > Pages > Branch main > Save.
  Membuka index.html langsung dengan klik ganda juga bisa. Peta dasar butuh internet.

CATATAN
  - Target titik per zona: sampai 900 ha = 3, 901-1250 ha = 4, di atas 1250 ha = 5.
  - Kualitas data: Valid (RSD 30% atau kurang, minimal 3 titik), Revisi (RSD di atas 30%), Kurang (1-2 titik), Belum (0 titik).
  - Bila zona di-merge lagi, geometri (zona_geo.js) perlu dibuat ulang.
  - Tombol "Muat file DBF" di dashboard memuat DBF langsung di browser untuk dicoba, tanpa mengubah data.js.
