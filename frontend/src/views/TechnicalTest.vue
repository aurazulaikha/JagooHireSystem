<template>
  <div class="dashboard-wrapper">
    <div class="dashboard-container">
      <!-- Header -->
      <div class="dashboard-header">
        <h1 class="dashboard-title">Technical Test</h1>
        <div class="title-underline"></div>
      </div>

      <!-- Actions Bar -->
      <div class="actions-bar">
        <input
          type="text"
          v-model="searchQuery"
          placeholder="Cari technical test..."
          class="search-input"
        />
      </div>

      <!-- ========== TABEL 1: BELUM MELAKUKAN TECHNICAL TEST ========== -->
      <p class="dashboard-subtitle">Belum Melakukan Technical Test</p>
      <div class="table-scroll-wrapper">
      <table class="request-table">
        <thead>
          <tr>
            <th>No</th>
            <th>Request Candidate ID</th>
            <th>Nama Kandidat</th>
            <th>Role Dilamar</th>
            <th>Role Dibutuhkan</th>
            <th>Email Kandidat</th>
            <th>Hp/Telp</th>
            <th>Domisili</th>
            <th>Perusahaan</th>
            <th>Lokasi Kerja</th>
            <th>Metode Kerja</th>
            <th>Jadwal Kerja</th>
            <th>Level</th>
            <th>Aptitude Score</th>
            <th>Candidate Status</th>
            <th v-if="userRole === 'AM'">Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(p, index) in pendingTechnical"
            :key="p.request_candidate_id"
          >
            <td>{{ index + 1 }}</td>
            <td>{{ p.request_candidate_id }}</td>
            <td>{{ p.candidate_name }}</td>
            <td>{{ p.applied_role }}</td>
            <td>{{ p.requested_role }}</td>
            <td>{{ p.candidate_email }}</td>
            <td>{{ p.no_telp }}</td>
            <td>{{ p.domisili }}</td>
            <td>{{ p.company_name }}</td>
            <td>{{ p.location }}</td>
            <td>{{ p.work_method }}</td>
            <td>{{ p.work_schedule }}</td>
            <td>{{ p.level }}</td>
            <td>{{ p.aptitude_score }}</td>
            <td>{{ p.candidate_status }}</td>
            <td v-if="userRole === 'AM'">
              <button
                class="btn-edit"
                @click="goToTechnicalTest(p.request_candidate_id)"
              >
                Buat Tes
              </button>
            </td>
          </tr>
          <tr v-if="pendingTechnical.length === 0">
            <td colspan="16" class="text-center">
              Tidak ada kandidat yang menunggu technical test.
            </td>
          </tr>
        </tbody>
      </table>
      </div>

      <br />

      <!-- ========== TABEL 2: SUDAH MELAKUKAN TECHNICAL TEST ========== -->
      <h2 class="dashboard-subtitle">Sudah Melakukan Technical Test</h2>
      <div class="table-scroll-wrapper">
      <table class="request-table">
        <thead>
          <tr>
            <th>No</th>
            <th>Request Candidate ID</th>
            <th>Nama Kandidat</th>
            <th>Role Dilamar</th>
            <th>Role Dibutuhkan</th>
            <th>Email Kandidat</th>
            <th>Hp/Telp</th>
            <th>Domisili</th>
            <th>Perusahaan</th>
            <th>Lokasi Kerja</th>
            <th>Metode Kerja</th>
            <th>Jadwal Kerja</th>
            <th>Level</th>
            <th>Tanggal Tes</th>
            <th>Aptitude Score</th>
            <th>Candidate Status</th>
            <th>Lanjut?</th>
            <th>Domain 1 & 2 Score</th>
            <th>Notes</th>
            <th>Portfolio Eval</th>
            <th>Stack Eval</th>
            <th>Candidate Data Created At</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(t, index) in doneTechnical" :key="t.id">
            <td>{{ index + 1 }}</td>
            <td>{{ t.request_candidate_id }}</td>
            <td>{{ t.candidate_name }}</td>
            <td>{{ t.applied_role }}</td>
            <td>{{ t.requested_role }}</td>
            <td>{{ t.candidate_email }}</td>
            <td>{{ t.no_telp }}</td>
            <td>{{ t.domisili }}</td>
            <td>{{ t.company_name }}</td>
            <td>{{ t.location }}</td>
            <td>{{ t.work_method }}</td>
            <td>{{ t.work_schedule }}</td>
            <td>{{ t.level }}</td>
            <td>{{ formatDate(t.test_date) }}</td>
            <td>{{ t.aptitude_score }}</td>
            <td>{{ t.candidate_status }}</td>
            <td>{{ t.continue_next }}</td>
            <td>{{ t.domain12_score }}</td>
            <td>{{ t.notes }}</td>
            <td>{{ t.portfolio_eval }}</td>
            <td>{{ t.stack_eval }}</td>
            <td>{{ formatDate(t.test_created_at) }}</td>
          </tr>
          <tr v-if="doneTechnical.length === 0">
            <td colspan="22" class="text-center">
              Belum ada kandidat yang melakukan technical test.
            </td>
          </tr>
        </tbody>
      </table>
    </div>

      <!-- Pagination -->
      <div class="pagination" v-if="totalPages > 1">
        <button :disabled="currentPage === 1" @click="currentPage--">
          Prev
        </button>
        <span>Halaman {{ currentPage }} dari {{ totalPages }}</span>
        <button :disabled="currentPage === totalPages" @click="currentPage++">
          Next
        </button>
      </div>

      <!-- Alert -->
      <div v-if="showAlert" class="alert-overlay">
        <div class="alert-box">
          <p>{{ alertMessage }}</p>
          <button @click="closeAlert">OK</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "TechnicalTestList",
  data() {
    const user = JSON.parse(localStorage.getItem("user")) || {};
    return {
      tests: [],
      searchQuery: "",
      token: user.token || "",
      userRole: user.role || "",
      pendingTechnical: [],
      doneTechnical: [],

      perPage: 10,
      currentPage: 1,
      showAlert: false,
      alertMessage: "",
    };
  },
  computed: {
    filteredTests() {
      const q = this.searchQuery.toLowerCase();
      return this.tests.filter(
        (t) =>
          t.request_candidate_id.toString().includes(q) ||
          (t.stack_eval && t.stack_eval.toLowerCase().includes(q)) ||
          (t.portfolio_eval && t.portfolio_eval.toLowerCase().includes(q)) ||
          (t.notes && t.notes.toLowerCase().includes(q))
      );
    },
    paginatedTests() {
      const start = (this.currentPage - 1) * this.perPage;
      return this.filteredTests.slice(start, start + this.perPage);
    },
    totalPages() {
      return Math.ceil(this.filteredTests.length / this.perPage);
    },
  },
  mounted() {
    this.getTechnicalOverview();
  },

  methods: {
    async getTechnicalOverview() {
      try {
        const res = await axios.get(
          "http://localhost:5000/technical_tests/overview",
          {
            headers: { Authorization: `Bearer ${this.token}` },
          }
        );
        this.pendingTechnical = res.data.pending_technical;
        this.doneTechnical = res.data.done_technical;
      } catch (err) {
        console.error(err);
        this.showCustomAlert("Gagal memuat data overview technical test.");
      }
    },

    editTest(id) {
      this.$router.push({ name: "EditTechnicalTest", params: { id } });
    },
    async deleteTest(id) {
      try {
        await axios.delete(`http://localhost:5000/technical_tests/${id}`, {
          headers: { Authorization: `Bearer ${this.token}` },
        });
        this.showCustomAlert("Technical test berhasil dihapus!");
        this.getTechnicalTests();
      } catch (err) {
        console.error(err);
        this.showCustomAlert("Gagal menghapus data.");
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return "-";
      const date = new Date(dateStr);
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
  },
};
</script>

<style scoped>
/* ===== TABLE SCROLL WRAPPER ===== */
.table-scroll-wrapper {
  width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  border-radius: 8px;
  -webkit-overflow-scrolling: touch;
  margin-top: 10px;
}

.table-scroll-wrapper::-webkit-scrollbar {
  height: 8px;
}

.table-scroll-wrapper::-webkit-scrollbar-thumb {
  background: #caa7a7;
  border-radius: 4px;
}

.table-scroll-wrapper::-webkit-scrollbar-thumb:hover {
  background: #a26060;
}
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
.dashboard-subtitle {
  font-size: 24px;
  font-weight: 700;
  color: #7a3e3e;
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

/* Table Styling */
.table-title {
  font-size: 22px;
  font-weight: 600;
  color: #7a3e3e;
  margin-top: 10px;
}
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
  background: #a62015;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}
.modal {
  background: white;
  padding: 25px;
  border-radius: 12px;
  width: 350px;
}
.modal label {
  display: block;
  margin-top: 10px;
  font-weight: 500;
}
.modal input,
.modal select {
  width: 100%;
  padding: 8px;
  border-radius: 6px;
  border: 1px solid #ccc;
  margin-top: 5px;
}
.modal-actions {
  margin-top: 15px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* Pagination */
.pagination {
  margin-top: 10px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
.pagination button {
  padding: 5px 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  background: #fff;
  cursor: pointer;
}
.pagination button:disabled {
  background: #eee;
  cursor: not-allowed;
}

/* Custom Alert & Confirm */
.alert-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  justify-content: center;
  align-items: center;
}
.alert-box {
  background: white;
  padding: 20px;
  border-radius: 12px;
  width: 300px;
  text-align: center;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
}
.alert-box button {
  margin-top: 15px;
  padding: 6px 12px;
  border: none;
  background: #a26060;
  color: white;
  border-radius: 6px;
  cursor: pointer;
}
.alert-actions {
  display: flex;
  justify-content: space-around;
  margin-top: 15px;
}
.alert-actions button {
  background: #a26060;
  color: white;
  padding: 6px 12px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
}
.alert-actions button:last-child {
  background: #ccc;
  color: #333;
}
</style>
