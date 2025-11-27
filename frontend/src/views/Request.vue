<template>
  <div class="dashboard-wrapper">
    <div class="dashboard-container">
      <!-- Header -->
      <div class="dashboard-header">
        <h1 class="dashboard-title">Manajemen Request</h1>
        <div class="title-underline"></div>
      </div>

      <!-- Actions Bar -->
      <div class="actions-bar">
        <input
          type="text"
          v-model="searchQuery"
          placeholder="Cari request..."
          class="search-input"
        />
        <button
          v-if="userRole === 'HCM'"
          class="btn-add"
          @click="goToAddRequest"
        >
          Tambah Request
        </button>
      </div>

      <!-- ============================ -->
      <!-- TABLE REQUESTS  -->
      <!-- ============================ -->

      <!-- WRAPPER SCROLL DITAMBAHKAN DI SINI -->
      <div class="table-scroll-request">
        <table class="request-table">
          <thead>
            <tr>
              <th>No</th>
              <th>ID</th>
              <th>Role Dibutuhkan</th>
              <th>Perusahaan</th>
              <th>Durasi</th>
              <th>Kuantitas</th>
              <th>Maks. Gaji</th>
              <th>Lokasi</th>
              <th>Metode Kerja</th>
              <th>Jadwal Kerja</th>
              <th>Level</th>
              <th>Tanggal Mulai</th>
              <th>Stage</th>
              <th>Job Description</th>
              <th v-if="userRole === 'HCM'">Aksi</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(req, index) in paginatedRequests" :key="req.id">
              <td>{{ index + 1 + (currentPage - 1) * perPage }}</td>
              <td>{{ req.id }}</td>
              <td>{{ req.role }}</td>
              <td>{{ req.company_name }}</td>
              <td>{{ req.duration }}</td>
              <td>{{ req.quantity }}</td>
              <td>{{ formatCurrency(req.max_salary) }}</td>
              <td>{{ req.location }}</td>
              <td>{{ req.work_method }}</td>
              <td>{{ req.work_schedule }}</td>
              <td>{{ req.level }}</td>
              <td>{{ formatDate(req.est_start_date) }}</td>
              <td>{{ req.current_stage }}</td>
              <td>{{ req.job_description }}</td>
              <td v-if="userRole === 'HCM'" class="actions-cell">
                <button class="btn-edit" @click="goToEditRequest(req.id)">Edit</button>
                <button class="btn-delete" @click="openConfirmDeleteRequest(req.id)">Hapus</button>
              </td>
            </tr>
            <tr v-if="filteredRequests.length === 0">
              <td :colspan="userRole === 'HCM' ? 15 : 14" class="text-center">
                Tidak ada request.
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination untuk Request -->
      <div class="pagination" v-if="totalPages > 1">
        <button :disabled="currentPage === 1" @click="currentPage--">Prev</button>
        <span>Halaman {{ currentPage }} dari {{ totalPages }}</span>
        <button :disabled="currentPage === totalPages" @click="currentPage++">Next</button>
      </div>

      <!-- ============================ -->
      <!-- TABLE REQUEST CANDIDATES -->
      <!-- ============================ -->

      <h2 class="sub-title">Daftar Kandidat Request</h2>

      <div class="actions-bar">
        <input
          type="text"
          v-model="searchQueryCandidate"
          placeholder="Cari kandidat request..."
          class="search-input"
        />
        <button
          v-if="['HCM'].includes(userRole)"
          class="btn-add"
          @click="goToAddRequestCandidate"
        >
          Tambah Kandidat Request
        </button>
      </div>

      <!-- WRAPPER SCROLL ORIGINAL -->
      <div class="table-scroll">
        <table class="request-candidate-table">
          <thead>
            <tr>
              <th>No</th>
              <th>Nama Kandidat</th>
              <th>Role Dilamar</th>
              <th>Role Dibutuhkan</th>
              <th>Email</th>
              <th>No. Telp</th>
              <th>Domisili</th>
              <th>Perusahaan</th>
              <th>Lokasi Kerja</th>
              <th>Metode Kerja</th>
              <th>Jadwal Kerja</th>
              <th>Level</th>
              <th>Durasi</th>
              <th>Kuantitas</th>
              <th>Maks. Gaji</th>
              <th>Stage</th>
              <th>Status Kandidat</th>
              <th v-if="['HCM'].includes(userRole)">Aksi</th>
            </tr>
          </thead>

          <tbody>
            <tr
              v-for="(rc, index) in paginatedRequestCandidates"
              :key="rc.request_candidate_id"
            >
              <td>{{ index + 1 + (currentPageCandidate - 1) * perPageCandidate }}</td>
              <td>{{ rc.nama_kandidat }}</td>
              <td>{{ rc.role_dilamar }}</td>
              <td>{{ rc.role_dibutuhkan }}</td>
              <td>{{ rc.email_kandidat }}</td>
              <td>{{ rc.no_telp }}</td>
              <td>{{ rc.domisili }}</td>
              <td>{{ rc.perusahaan }}</td>
              <td>{{ rc.lokasi_kerja }}</td>
              <td>{{ rc.metode_kerja }}</td>
              <td>{{ rc.jadwal_kerja }}</td>
              <td>{{ rc.level }}</td>
              <td>{{ rc.durasi }}</td>
              <td>{{ rc.kuantitas }}</td>
              <td>{{ formatCurrency(rc.maks_gaji) }}</td>
              <td>{{ rc.stage }}</td>
              <td>{{ rc.status_kandidat }}</td>

              <td v-if="['HCM'].includes(userRole)" class="actions-cell">
                <button class="btn-edit" @click="goToEditRequestCandidate(rc.request_candidate_id)">Edit</button>
                <button class="btn-delete" @click="openConfirmDeleteCandidate(rc.request_candidate_id)">Hapus</button>
              </td>
            </tr>

            <tr v-if="filteredRequestCandidates.length === 0">
              <td :colspan="['HCM'].includes(userRole) ? 18 : 17" class="text-center">
                Tidak ada kandidat request.
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination untuk Request Candidates -->
      <div class="pagination" v-if="totalPagesCandidate > 1">
        <button :disabled="currentPageCandidate === 1" @click="currentPageCandidate--">Prev</button>
        <span>Halaman {{ currentPageCandidate }} dari {{ totalPagesCandidate }}</span>
        <button :disabled="currentPageCandidate === totalPagesCandidate" @click="currentPageCandidate++">Next</button>
      </div>
    </div>

    <!-- ======================== -->
    <!-- POPUP ALERT -->
    <!-- ======================== -->
    <div v-if="showAlert" class="alert-overlay">
      <div class="alert-box">
        <p>{{ alertMessage }}</p>
        <button @click="closeAlert">OK</button>
      </div>
    </div>

    <!-- ======================== -->
    <!-- POPUP KONFIRMASI DELETE -->
    <!-- ======================== -->
    <div v-if="showConfirm" class="alert-overlay">
      <div class="alert-box">
        <p>{{ confirmMessage }}</p>
        <div class="alert-actions">
          <button @click="confirmYes">Ya</button>
          <button @click="confirmNo">Tidak</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "RequestsPage",
  data() {
    const user = JSON.parse(localStorage.getItem("user")) || {};
    return {
      requests: [],
      requestCandidates: [],
      searchQuery: "",
      searchQueryCandidate: "",
      token: user.token || "",
      userRole: user.role || "",
      perPage: 10,
      currentPage: 1,
      perPageCandidate: 10,
      currentPageCandidate: 1,
      alertMessage: "",
      showAlert: false,
      confirmMessage: "",
      showConfirm: false,
      confirmCallback: null,
    };
  },
  computed: {
    filteredRequests() {
      const q = this.searchQuery.toLowerCase();
      return this.requests.filter(
        (r) =>
          (r.role && r.role.toLowerCase().includes(q)) ||
          (r.company_name && r.company_name.toLowerCase().includes(q)) ||
          (r.location && r.location.toLowerCase().includes(q))
      );
    },
    paginatedRequests() {
      const start = (this.currentPage - 1) * this.perPage;
      return this.filteredRequests.slice(start, start + this.perPage);
    },
    totalPages() {
      return Math.ceil(this.filteredRequests.length / this.perPage) || 1;
    },
    filteredRequestCandidates() {
      const q = this.searchQueryCandidate.toLowerCase();
      return this.requestCandidates.filter(
        (rc) =>
          rc.nama_kandidat?.toLowerCase().includes(q) ||
          rc.role_dibutuhkan?.toLowerCase().includes(q) ||
          rc.perusahaan?.toLowerCase().includes(q)
      );
    },
    paginatedRequestCandidates() {
      const start = (this.currentPageCandidate - 1) * this.perPageCandidate;
      return this.filteredRequestCandidates.slice(start, start + this.perPageCandidate);
    },
    totalPagesCandidate() {
      return Math.ceil(this.filteredRequestCandidates.length / this.perPageCandidate) || 1;
    },
  },
  watch: {
    searchQuery() {
      this.currentPage = 1;
    },
    searchQueryCandidate() {
      this.currentPageCandidate = 1;
    },
  },
  mounted() {
    this.getRequests();
    this.getRequestCandidates();
  },
  methods: {
    async getRequests() {
      try {
        const res = await axios.get("http://localhost:5000/requests", {
          headers: { Authorization: `Bearer ${this.token}` },
        });
        this.requests = res.data || [];
      } catch (err) {
        console.error(err);
        this.showCustomAlert("Gagal mengambil data request.");
      }
    },
    async getRequestCandidates() {
      try {
        const res = await axios.get("http://localhost:5000/request_candidates", {
          headers: { Authorization: `Bearer ${this.token}` },
        });
        this.requestCandidates = res.data || [];
      } catch (err) {
        console.error(err);
        this.showCustomAlert("Gagal mengambil data kandidat request.");
      }
    },
    goToAddRequest() {
      this.$router.push("/add-request");
    },
    goToEditRequest(id) {
      this.$router.push({ name: "EditRequest", params: { id } });
    },
    goToAddRequestCandidate() {
      this.$router.push("/add-request-candidate");
    },
    goToEditRequestCandidate(id) {
      this.$router.push({ name: "EditRequestCandidate", params: { id } });
    },
    openConfirmDeleteRequest(id) {
      this.showCustomConfirm("Yakin ingin menghapus request ini?", async () => {
        try {
          await axios.delete(`http://localhost:5000/requests/${id}`, {
            headers: { Authorization: `Bearer ${this.token}` },
          });
          this.showCustomAlert("Request berhasil dihapus!");
          this.getRequests();
        } catch (err) {
          console.error(err);
          this.showCustomAlert("Gagal menghapus request.");
        }
      });
    },
    openConfirmDeleteCandidate(id) {
      this.showCustomConfirm("Yakin ingin menghapus kandidat request ini?", async () => {
        try {
          await axios.delete(`http://localhost:5000/request_candidates/${id}`, {
            headers: { Authorization: `Bearer ${this.token}` },
          });
          this.showCustomAlert("Kandidat request berhasil dihapus!");
          this.getRequestCandidates();
        } catch (err) {
          console.error(err);
          this.showCustomAlert("Gagal menghapus kandidat request.");
        }
      });
    },
    formatCurrency(value) {
      if (value === null || value === undefined) return "-";
      return new Intl.NumberFormat("id-ID", {
        style: "currency",
        currency: "IDR",
        maximumFractionDigits: 0,
      }).format(value || 0);
    },
    formatDate(dateStr) {
      if (!dateStr) return "-";
      const date = new Date(dateStr);
      if (isNaN(date.getTime())) return dateStr;
      return date.toLocaleString("id-ID", {
        day: "2-digit",
        month: "short",
        year: "numeric",
      });
    },
    showCustomAlert(message) {
      this.alertMessage = message;
      this.showAlert = true;
    },
    closeAlert() {
      this.showAlert = false;
    },
    showCustomConfirm(message, callback) {
      this.confirmMessage = message;
      this.confirmCallback = callback;
      this.showConfirm = true;
    },
    confirmYes() {
      if (this.confirmCallback) this.confirmCallback();
      this.showConfirm = false;
    },
    confirmNo() {
      this.showConfirm = false;
    },
  },
};
</script>

<style scoped>
/* ============================ */
/* FULL STYLE SESUAI KODE ASLI */
/* ============================ */

.dashboard-wrapper {
  background: linear-gradient(180deg, #f9f3f3, #fff);
  min-height: 100vh;
  display: flex;
  justify-content: center;
  padding: 100px 0 40px;
}

.dashboard-container {
  width: 90%;
  max-width: 1200px;
  color: #333;
  font-family: "Poppins", sans-serif;
  display: flex;
  flex-direction: column;
  gap: 25px;
}

/* Header */
.dashboard-title {
  font-size: 32px;
  font-weight: 700;
  color: #7a3e3e;
}
.title-underline {
  width: 80px;
  height: 4px;
  background: #a26060;
  border-radius: 5px;
  margin-bottom: 15px;
}

/* Actions Bar */
.actions-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.search-input {
  width: 250px;
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid #ccc;
}
.btn-add {
  background: #a26060;
  color: #fff;
  padding: 8px 14px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  border: none;
}
.btn-add:hover {
  background: #7a3e3e;
}

/* ===== TABLE REQUEST  */
.request-table {
  width: 100%;
  border-collapse: collapse;
  border: 1px solid #e0d5d5;
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
}
.request-table th,
.request-table td {
  padding: 12px 10px;
  text-align: center;
  border-bottom: 1px solid #eee;
}
.request-table th {
  background-color: #a26060;
  color: #fff;
  font-weight: 600;
}
.request-table tbody tr:nth-child(even) {
  background-color: #faf6f6;
}
.request-table tbody tr:hover {
  background-color: #f5eaea;
  transition: 0.3s;
}
.text-center {
  text-align: center;
}

/* ===== TABLE REQUEST CANDIDATE  ===== */
.sub-title {
  font-size: 24px;
  font-weight: 700;
  color: #7a3e3e;
  margin-top: 30px;
}

.table-scroll {
  width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
  border-radius: 12px;
  scrollbar-width: thin;
  scrollbar-color: #c1a5a5 #f3eaea;
}
.table-scroll::-webkit-scrollbar {
  height: 8px;
}
.table-scroll::-webkit-scrollbar-thumb {
  background-color: #c1a5a5;
  border-radius: 10px;
}
.table-scroll::-webkit-scrollbar-track {
  background-color: #f3eaea;
}

/* Table khusus untuk Request Candidate */
.request-candidate-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1300px; /* Lebar minimum untuk scroll */
  background: #fff;
}
.request-candidate-table th,
.request-candidate-table td {
  padding: 12px 8px;
  text-align: center;
  border-bottom: 1px solid #eee;
  font-size: 13px;
}
.request-candidate-table th {
  background-color: #a26060;
  color: #fff;
  font-weight: 600;
  white-space: nowrap;
}
.request-candidate-table tbody tr:nth-child(even) {
  background-color: #faf6f6;
}
.request-candidate-table tbody tr:hover {
  background-color: #f5eaea;
  transition: 0.3s;
}

/* Button Actions */
.actions-cell {
  display: flex;
  justify-content: center;
  gap: 10px;
}
.btn-edit {
  background: #43a032;
  color: #fff;
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}
.btn-edit:hover {
  background: #2e7d1f;
}
.btn-delete {
  background: #d33226;
  color: #fff;
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}
.btn-delete:hover {
  background: #a11f1a;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  margin-top: 10px;
}
.pagination button {
  padding: 6px 12px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-weight: 600;
}
.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ======================== */
/* ALERT POPUP */
.alert-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.alert-box {
  background: #fff;
  padding: 20px 25px;
  border-radius: 12px;
  max-width: 350px;
  text-align: center;
  font-weight: 500;
}
.alert-box button {
  margin-top: 15px;
  padding: 6px 16px;
  border: none;
  background: #a26060;
  color: #fff;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}
.alert-box button:hover {
  background: #7a3e3e;
}
.alert-actions {
  display: flex;
  justify-content: space-around;
  margin-top: 15px;
}
.alert-actions button {
  min-width: 80px;
}

/* ======================== */
/* SCROLL BAR REQUEST TABLE */
.table-scroll-request {
  overflow-x: auto;
  border-radius: 12px;
  scrollbar-width: thin;
  scrollbar-color: #c1a5a5 #f3eaea;
}
.table-scroll-request::-webkit-scrollbar {
  height: 8px;
}
.table-scroll-request::-webkit-scrollbar-thumb {
  background-color: #c1a5a5;
  border-radius: 10px;
}
.table-scroll-request::-webkit-scrollbar-track {
  background-color: #f3eaea;
}
</style>
