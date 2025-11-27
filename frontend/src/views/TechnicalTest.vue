<template>
  <div class="dashboard-wrapper">
    <div class="dashboard-container">
      <!-- Header -->
      <div class="dashboard-header">
        <h1 class="dashboard-title">Technical Test</h1>
        <div class="title-underline"></div>
      </div>

      <!-- Search Bar -->
      <div class="search-bar">
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
        <table class="technical-table">
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
              <th>Level Dibutuhkan</th>
              <th>Aptitude Score</th>
              <th>Candidate Status</th>
              <th>Tanggal Tes</th>
              <th v-if="userRole === 'AM'">Aksi</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(p, index) in paginatedPending" :key="p.rc_id">
              <td>{{ (currentPagePending - 1) * itemsPerPage + index + 1 }}</td>
              <td>{{ p.rc_id }}</td>
              <td>{{ p.candidate_name }}</td>
              <td>{{ p.applied_role }}</td>
              <td>{{ p.requested_role }}</td>
              <td>
                <a v-if="p.candidate_email" :href="`mailto:${p.candidate_email}`">
                  {{ p.candidate_email }}
                </a>
                <span v-else>—</span>
              </td>
              <td>{{ p.no_telp }}</td>
              <td>{{ p.domisili }}</td>
              <td>{{ p.company_name }}</td>
              <td>{{ p.location }}</td>
              <td>{{ p.work_method }}</td>
              <td>{{ p.work_schedule }}</td>
              <td>{{ p.level }}</td>
              <td>{{ p.aptitude_score }}</td>
              <td>{{ p.candidate_status }}</td>
              <td>{{ p.test_date ? formatDate(p.test_date) : "-" }}</td>
              <td v-if="userRole === 'AM'" class="actions-cell">
                <button class="btn-edit" @click="openScheduleModal(p)">
                  Atur Jadwal
                </button>
                <button class="btn-edit" @click="goToPenilaian(p)">
                  Penilaian
                </button>
              </td>
            </tr>
            <tr v-if="paginatedPending.length === 0">
              <td colspan="17" class="text-center">
                Tidak ada kandidat yang menunggu technical test.
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination untuk tabel belum test -->
      <div class="pagination" v-if="totalPagesPending > 1">
        <button :disabled="currentPagePending === 1" @click="currentPagePending--">
          Prev
        </button>
        <span>Halaman {{ currentPagePending }} dari {{ totalPagesPending }}</span>
        <button :disabled="currentPagePending === totalPagesPending" @click="currentPagePending++">
          Next
        </button>
      </div>

      <br />

      <!-- ========== TABEL 2: SUDAH MELAKUKAN TECHNICAL TEST ========== -->
      <h2 class="dashboard-subtitle">Sudah Melakukan Technical Test</h2>
      <div class="table-scroll-wrapper">
        <table class="technical-table">
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
              <th>Level Dibutuhkan</th>
              <th>Tanggal Tes</th>
              <th>Aptitude Score</th>
              <th>Candidate Status</th>
              <th>Lanjut?</th>
              <th>Domain 1 & 2 Score</th>
              <th>Notes</th>
              <th>Portfolio Eval</th>
              <th>Stack Eval</th>
              <th>Candidate Data Created At</th>
              <th v-if="userRole === 'AM'">Aksi</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(t, index) in paginatedDone" :key="t.technical_test_id">
              <td>{{ (currentPageDone - 1) * itemsPerPage + index + 1 }}</td>
              <td>{{ t.rc_id }}</td>
              <td>{{ t.candidate_name }}</td>
              <td>{{ t.applied_role }}</td>
              <td>{{ t.requested_role }}</td>
              <td>
                <a v-if="t.candidate_email" :href="`mailto:${t.candidate_email}`">
                  {{ t.candidate_email }}
                </a>
                <span v-else>—</span>
              </td>
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
              <td>
                <span :class="['status-badge', getContinueNextClass(t.continue_next)]">
                  {{ t.continue_next }}
                </span>
              </td>
              <td>{{ t.domain12_score }}</td>
              <td>{{ t.notes }}</td>
              <td>{{ t.portfolio_eval }}</td>
              <td>{{ t.stack_eval }}</td>
              <td>{{ formatDate(t.test_created_at) }}</td>
              <td v-if="userRole === 'AM'" class="actions-cell">
                <button class="btn-edit" @click="editTest(t)">
                  Edit
                </button>
                <button class="btn-delete" @click="deleteTest(t)">
                  Hapus
                </button>
              </td>
            </tr>
            <tr v-if="paginatedDone.length === 0">
              <td :colspan="emptyRowColspan" class="text-center">
                Belum ada kandidat yang melakukan technical test.
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination untuk tabel sudah test -->
      <div class="pagination" v-if="totalPagesDone > 1">
        <button :disabled="currentPageDone === 1" @click="currentPageDone--">Prev</button>
        <span>Halaman {{ currentPageDone }} dari {{ totalPagesDone }}</span>
        <button :disabled="currentPageDone === totalPagesDone" @click="currentPageDone++">Next</button>
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

  <!-- ATUR JADWAL -->
  <div v-if="showScheduleModal" class="modal-overlay-schedule">
    <div class="alert-box">
      <h3>Atur Jadwal Technical Test</h3>
      <p><strong>Kandidat:</strong> {{ selectedCandidate.candidate_name }}</p>
      <input v-model="scheduleDate" type="date" />
      <div class="alert-actions">
        <button @click="saveSchedule">Simpan</button>
        <button @click="closeScheduleModal">Batal</button>
      </div>
    </div>
  </div>

  <!-- POPUP HAPUS -->
  <div v-if="showDeleteModal" class="modal-overlay-schedule">
    <div class="alert-box">
      <h3>Hapus Data Technical Test</h3>
      <p><strong>Konfirmasi Penghapusan</strong></p>
      <p>Apakah Anda yakin ingin menghapus data technical test untuk:</p>
      <p>
        <strong>{{ candidateToDelete?.candidate_name }}</strong>
      </p>
      <p>Data yang dihapus tidak dapat dikembalikan.</p>
      <div class="alert-actions">
        <button @click="confirmDelete" class="btn-delete">Hapus</button>
        <button @click="closeDeleteModal">Batal</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "TechnicalTest",
  data() {
    const user = JSON.parse(localStorage.getItem("user")) || {};
    return {
      searchQuery: "",
      token: user.token || "",
      userRole: user.role || "",
      pendingTechnical: [],
      doneTechnical: [],
      currentPagePending: 1,
      currentPageDone: 1,
      itemsPerPage: 10,
      showAlert: false,
      alertMessage: "",
      showScheduleModal: false,
      selectedCandidate: {},
      scheduleDate: "",
      showDeleteModal: false,
      candidateToDelete: null,
    };
  },
  computed: {
    filteredPending() {
      const query = this.searchQuery.toLowerCase();
      return this.pendingTechnical.filter(p => 
        p.candidate_name?.toLowerCase().includes(query) ||
        String(p.rc_id).includes(query) ||
        p.applied_role?.toLowerCase().includes(query) ||
        p.requested_role?.toLowerCase().includes(query)
      );
    },
    filteredDone() {
      const query = this.searchQuery.toLowerCase();
      return this.doneTechnical.filter(t =>
        t.candidate_name?.toLowerCase().includes(query) ||
        String(t.rc_id).includes(query) ||
        t.applied_role?.toLowerCase().includes(query) ||
        t.requested_role?.toLowerCase().includes(query)
      );
    },
    paginatedPending() {
      const start = (this.currentPagePending - 1) * this.itemsPerPage;
      return this.filteredPending.slice(start, start + this.itemsPerPage);
    },
    totalPagesPending() {
      return Math.ceil(this.filteredPending.length / this.itemsPerPage);
    },
    paginatedDone() {
      const start = (this.currentPageDone - 1) * this.itemsPerPage;
      return this.filteredDone.slice(start, start + this.itemsPerPage);
    },
    totalPagesDone() {
      return Math.ceil(this.filteredDone.length / this.itemsPerPage);
    },
    emptyRowColspan() {
      return this.userRole === "AM" ? 23 : 22;
    },
  },
  watch: {
    searchQuery() {
      this.currentPagePending = 1;
      this.currentPageDone = 1;
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
        this.showCustomAlert("Gagal memuat data overview technical test.");
      }
    },
    openScheduleModal(candidate) {
      this.selectedCandidate = candidate;
      this.scheduleDate = candidate.test_date ? 
        new Date(candidate.test_date).toISOString().substr(0, 10) : "";
      this.showScheduleModal = true;
    },
    closeScheduleModal() {
      this.showScheduleModal = false;
      this.selectedCandidate = {};
      this.scheduleDate = "";
    },
    async saveSchedule() {
      if (!this.scheduleDate) {
        return this.showCustomAlert("Silakan pilih tanggal terlebih dahulu!");
      }

      try {
        await axios.patch(
          "http://localhost:5000/technical_tests/schedule",
          {
            rc_id: this.selectedCandidate.rc_id,
            test_date: this.scheduleDate,
          },
          { headers: { Authorization: `Bearer ${this.token}` } }
        );
        this.showCustomAlert("Jadwal tes berhasil disimpan!");
        await this.getTechnicalOverview(); // refresh tabel
        this.closeScheduleModal();
      } catch (err) {
        this.showCustomAlert("Gagal menyimpan jadwal tes.");
      }
    },
    async goToPenilaian(candidate) {
      const res = await axios.get(
        `http://localhost:5000/technical_tests/${candidate.rc_id}`,
        { headers: { Authorization: `Bearer ${this.token}` } }
      );

      const existing = res.data[0] || {};

      localStorage.setItem(
        "selectedCandidate",
        JSON.stringify({
          rc_id: candidate.rc_id,
          candidate_name: candidate.candidate_name,
          test_date: existing.test_date || "",
        })
      );

      this.$router.push("/technical-test/penilaian");
    },
    editTest(test) {
      const testDate = test.test_date ? 
        new Date(test.test_date).toISOString().split("T")[0] : "";

      localStorage.setItem(
        "selectedCandidate",
        JSON.stringify({
          rc_id: test.rc_id,
          candidate_name: test.candidate_name,
          test_date: testDate,
          domain12_score: test.domain12_score || "",
          notes: test.notes || "",
          portfolio_eval: test.portfolio_eval || "",
          stack_eval: test.stack_eval || "",
          continue_next: test.continue_next || "",
          technical_test_id: test.technical_test_id || null,
          mode: "edit",
        })
      );

      this.$router.push("/technical-test/penilaian");
    },
    deleteTest(test) {
      this.candidateToDelete = test;
      this.showDeleteModal = true;
    },
    async confirmDelete() {
      if (!this.candidateToDelete) return;

      try {
        await axios.delete(
          `http://localhost:5000/technical_tests/${this.candidateToDelete.technical_test_id}`,
          {
            headers: { Authorization: `Bearer ${this.token}` },
          }
        );

        this.showCustomAlert("Data technical test berhasil dihapus!");
        await this.getTechnicalOverview(); // refresh data
        this.closeDeleteModal();
      } catch (err) {
        this.showCustomAlert("Gagal menghapus data technical test.");
      }
    },
    closeDeleteModal() {
      this.showDeleteModal = false;
      this.candidateToDelete = null;
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
    getContinueNextClass(value) {
      if (!value) return "";
      const v = String(value).toLowerCase();
      if (v === "ya") return "cell-green";
      if (v === "tidak") return "cell-red";
      return "";
    },
  },
};
</script>

<style scoped>
/* TABLE SCROLL WRAPPER */
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

/* Search Bar */
.search-bar {
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

/* Table Styling */
.technical-table {
  width: 100%;
  border-collapse: collapse;
  border: 1px solid #e0d5d5;
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
}
.technical-table th,
.technical-table td {
  padding: 12px 10px;
  text-align: center;
  border-bottom: 1px solid #eee;
}
.technical-table th {
  background-color: #a26060;
  color: #fff;
  font-weight: 600;
}
.technical-table tbody tr:nth-child(even) {
  background-color: #faf6f6;
}
.technical-table tbody tr:hover {
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
.modal-overlay-schedule {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9000; /* LEBIH RENDAH */
}

/* Date */
input[type="date"] {
  width: 70%;
  padding: 8px;
  border-radius: 6px;
  border: 1px solid #ccc;
  margin-top: 5px;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-top: 10px;
  gap: 10px;
}
.pagination button {
  padding: 5px 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  background: #fff;
  cursor: pointer;
  transition: all 0.3s ease;
}
.pagination button:hover {
  background: #a26060;
  color: white;
  border-color: #a26060;
}
.pagination button:disabled {
  background: #eee;
  color: #999;
  cursor: not-allowed;
}

/* Custom Alert & Confirm */
.alert-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.25);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}
.alert-box {
  background: white;
  padding: 20px;
  border-radius: 12px;
  width: 300px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
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

/* Badge */
.status-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  text-transform: capitalize;
  color: white;
  min-width: 70px;
  text-align: center;
}
.status-badge.cell-green {
  background-color: #0c8c41;
}
.status-badge.cell-red {
  background-color: #ab2929;
}
</style>
