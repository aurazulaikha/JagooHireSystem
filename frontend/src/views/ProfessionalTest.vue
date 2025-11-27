<template>
  <div class="dashboard-wrapper">
    <div class="dashboard-container">
      <!-- Header -->
      <div class="dashboard-header">
        <h1 class="dashboard-title">Professional Test</h1>
        <div class="title-underline"></div>
      </div>

      <!-- Actions Bar -->
      <div class="actions-bar">
        <input
          type="text"
          v-model="searchQuery"
          placeholder="Cari professional test..."
          class="search-input"
        />
      </div>

      <!-- ========== TABEL 1: BELUM MELAKUKAN PROFESSIONAL TEST ========== -->
      <p class="dashboard-subtitle">Belum Melakukan Professional Test</p>
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
              <th>Level Dibutuhkan</th>
              <th>Aptitude Score</th>
              <th>Technical Score</th>
              <th>Candidate Status</th>
              <th>Tanggal Tes</th>
              <th v-if="userRole === 'Director'">Aksi</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(p, index) in filteredPending"
              :key="p.request_candidate_id"
            >
              <td>{{ index + 1 }}</td>
              <td>{{ p.request_candidate_id }}</td>
              <td>{{ p.candidate_name }}</td>
              <td>{{ p.applied_role }}</td>
              <td>{{ p.requested_role }}</td>
              <td>
                <a
                  v-if="p.candidate_email"
                  :href="`mailto:${p.candidate_email}`"
                >
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
              <td>{{ p.technical_score }}</td>
              <td>{{ p.candidate_status }}</td>
              <td>{{ p.test_date ? formatDate(p.test_date) : "-" }}</td>
              <td v-if="userRole === 'Director'" class="actions-cell">
                <button class="btn-schedule" @click="openScheduleModal(p)">
                  Set Tanggal
                </button>
                <button class="btn-edit" @click="goToPenilaian(p)">
                  Penilaian
                </button>
              </td>
            </tr>
            <tr v-if="filteredPending.length === 0">
              <td colspan="18" class="text-center">
                Tidak ada kandidat yang menunggu professional test.
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <br />

      <!-- ========== TABEL 2: SUDAH MELAKUKAN PROFESSIONAL TEST ========== -->
      <h2 class="dashboard-subtitle">Sudah Melakukan Professional Test</h2>
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
              <th>Level Dibutuhkan</th>
              <th>Tanggal Tes</th>
              <th>Aptitude Score</th>
              <th>Technical Score</th>
              <th>Candidate Status</th>
              <th>Programming Fundamentals</th>
              <th>Software Engineering</th>
              <th>Portfolio Eval</th>
              <th>Communication</th>
              <th>Adaptability</th>
              <th>Discipline</th>
              <th>Commitment</th>
              <th>Final Result</th>
              <th>Notes</th>
              <th v-if="userRole === 'Director'">Aksi</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(t, index) in filteredDone" :key="t.professional_test_id">
              <td>{{ index + 1 }}</td>
              <td>{{ t.request_candidate_id }}</td>
              <td>{{ t.candidate_name }}</td>
              <td>{{ t.applied_role }}</td>
              <td>{{ t.requested_role }}</td>
              <td>
                <a
                  v-if="t.candidate_email"
                  :href="`mailto:${t.candidate_email}`"
                >
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
              <td>{{ t.technical_score }}</td>
              <td>{{ t.candidate_status }}</td>
              <td>{{ t.programming_fundamentals }}</td>
              <td>{{ t.software_engineering }}</td>
              <td>{{ t.portfolio_eval }}</td>
              <td>{{ t.communication }}</td>
              <td>{{ t.adaptability }}</td>
              <td>{{ t.discipline }}</td>
              <td>{{ t.commitment }}</td>
              <td>
                <span
                  :class="[
                    'status-badge',
                    getFinalResultClass(t.final_result),
                  ]"
                >
                  {{ formatFinalResult(t.final_result) }}
                </span>
              </td>
              <td>{{ t.notes }}</td>
              <td v-if="userRole === 'Director'" class="actions-cell">
                <button class="btn-edit" @click="editTest(t)">Edit</button>
                <button class="btn-delete" @click="deleteTest(t)">Hapus</button>
              </td>
            </tr>
            <tr v-if="filteredDone.length === 0">
              <td :colspan="userRole === 'Director' ? 27 : 26" class="text-center">
                Belum ada kandidat yang melakukan professional test.
              </td>
            </tr>
          </tbody>
        </table>
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
      <h3>Set Tanggal Professional Test</h3>
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
      <h3>Hapus Data Professional Test</h3>
      <p><strong>Konfirmasi Penghapusan</strong></p>
      <p>Apakah Anda yakin ingin menghapus data professional test untuk:</p>
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
  name: "ProfessionalTest",
  data() {
    const user = JSON.parse(localStorage.getItem("user")) || {};
    return {
      searchQuery: "",
      token: user.token || "",
      userRole: user.role || "",
      pendingProfessional: [],
      doneProfessional: [],

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
      const q = this.searchQuery.toLowerCase();
      return this.pendingProfessional.filter(
        (p) =>
          (p.candidate_name || "").toLowerCase().includes(q) ||
          String(p.request_candidate_id).includes(q) ||
          (p.applied_role || "").toLowerCase().includes(q) ||
          (p.requested_role || "").toLowerCase().includes(q)
      );
    },

    filteredDone() {
      const q = this.searchQuery.toLowerCase();
      return this.doneProfessional.filter(
        (t) =>
          (t.candidate_name || "").toLowerCase().includes(q) ||
          String(t.request_candidate_id).includes(q) ||
          (t.applied_role || "").toLowerCase().includes(q) ||
          (t.requested_role || "").toLowerCase().includes(q)
      );
    }
  },
  mounted() {
    this.getProfessionalOverview();
  },

  methods: {
    async getProfessionalOverview() {
      try {
        const res = await axios.get(
          "http://localhost:5000/professional_tests/overview",
          {
            headers: { Authorization: `Bearer ${this.token}` },
          }
        );
        
        this.pendingProfessional = res.data.pending_professional || [];
        this.doneProfessional = res.data.done_professional || [];

        console.log("Pending Professional:", this.pendingProfessional);
        console.log("Done Professional:", this.doneProfessional);

      } catch (err) {
        console.error(err);
        this.showCustomAlert("Gagal memuat data overview professional test.");
      }
    },

    openScheduleModal(candidate) {
      this.selectedCandidate = candidate;
      this.scheduleDate = candidate.test_date
        ? new Date(candidate.test_date).toISOString().substr(0, 10)
        : "";
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
          "http://localhost:5000/professional_tests/schedule",
          {
            request_candidate_id: this.selectedCandidate.request_candidate_id,
            test_date: this.scheduleDate,
          },
          { headers: { Authorization: `Bearer ${this.token}` } }
        );
        
        this.showCustomAlert("Jadwal tes berhasil disimpan!");
        await this.getProfessionalOverview();
        this.closeScheduleModal();
      } catch (err) {
        console.error(err);
        this.showCustomAlert("Gagal menyimpan jadwal tes.");
      }
    },

    async goToPenilaian(candidate) {
  try {
    const res = await axios.get(
      `http://localhost:5000/professional_tests/${candidate.request_candidate_id}`,
      { headers: { Authorization: `Bearer ${this.token}` } }
    );

    const existing = res.data || {};

    // PERBAIKAN: Simpan SEMUA data yang diperlukan
    localStorage.setItem(
      "selectedCandidate",
      JSON.stringify({
        // Data identitas
        request_candidate_id: candidate.request_candidate_id,
        candidate_name: candidate.candidate_name,
        
        // Data tanggal - prioritaskan yang existing
        test_date: existing.test_date || candidate.test_date || "",
        
        // Data scores
        aptitude_score: existing.aptitude_score || candidate.aptitude_score,
        technical_score: candidate.technical_score,
        
        // Data professional test yang sudah ada
        programming_fundamentals: existing.programming_fundamentals || "",
        software_engineering: existing.software_engineering || "",
        portfolio_eval: existing.portfolio_eval || "",
        communication: existing.communication || "",
        adaptability: existing.adaptability || "",
        discipline: existing.discipline || "",
        commitment: existing.commitment || "",
        final_result: existing.final_result || "",
        notes: existing.notes || "",
        
        // Metadata untuk edit
        professional_test_id: existing.id || null,
        mode: existing.id ? "edit" : "add"
      })
    );

    this.$router.push("/professional-test/penilaian");
  } catch (err) {
    console.error(err);
    this.showCustomAlert("Gagal mengambil data penilaian.");
  }
},

    editTest(test) {
      localStorage.setItem(
        "selectedCandidate",
        JSON.stringify({
          request_candidate_id: test.request_candidate_id,
          candidate_name: test.candidate_name,
          test_date: test.test_date
            ? new Date(test.test_date).toISOString().split("T")[0]
            : "",
          aptitude_score: test.aptitude_score || "",
          programming_fundamentals: test.programming_fundamentals || "",
          software_engineering: test.software_engineering || "",
          portfolio_eval: test.portfolio_eval || "",
          communication: test.communication || "",
          adaptability: test.adaptability || "",
          discipline: test.discipline || "",
          commitment: test.commitment || "",
          final_result: test.final_result || "",
          notes: test.notes || "",
          professional_test_id: test.professional_test_id || null,
          mode: "edit"
        })
      );

      this.$router.push("/professional-test/penilaian");
    },

    deleteTest(test) {
      this.candidateToDelete = test;
      this.showDeleteModal = true;
    },

    async confirmDelete() {
      if (!this.candidateToDelete) return;

      try {
        await axios.delete(
          `http://localhost:5000/professional_tests/${this.candidateToDelete.professional_test_id}`,
          {
            headers: { Authorization: `Bearer ${this.token}` },
          }
        );

        this.showCustomAlert("Data professional test berhasil dihapus!");
        await this.getProfessionalOverview();
        this.closeDeleteModal();
      } catch (err) {
        console.error(err);
        this.showCustomAlert("Gagal menghapus data professional test.");
        this.closeDeleteModal();
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

    formatFinalResult(value) {
      if (value === 'lulus') return 'Lulus';
      if (value === 'tidak_lulus') return 'Tidak Lulus';
      return value;
    },
    
    showCustomAlert(message) {
      this.alertMessage = message;
      this.showAlert = true;
    },
    
    closeAlert() {
      this.showAlert = false;
    },
    
    getFinalResultClass(value) {
      if (!value) return "";
      const v = String(value).toLowerCase();
      if (v === "lulus") return "cell-green";
      if (v === "tidak_lulus") return "cell-red";
      return "";
    },
  },
};
</script>

<style scoped>
/* TOMBOL STYLING */
.btn-schedule {
  background: #a26060;
  color: #fff;
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  margin-right: 5px;
}

.btn-schedule:hover {
  background: #7a3e3e;
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

.actions-cell {
  display: flex;
  justify-content: center;
  gap: 10px;
}

/* STYLE LAINNYA */
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

.modal-overlay-schedule {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9000;
}

.alert-box {
  background: white;
  padding: 20px;
  border-radius: 12px;
  width: 300px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
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

.alert-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.25);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}
</style>