<template>
  <div class="dashboard-wrapper">
    <div class="dashboard-container">
      <!-- Header -->
      <div class="dashboard-header">
        <h1 class="dashboard-title">Manajemen Kandidat</h1>
        <div class="title-underline"></div>
      </div>

      <!-- Actions Bar -->
      <div class="actions-bar">
        <input
          type="text"
          v-model="searchQuery"
          placeholder="Cari kandidat..."
          class="search-input"
        />
        <button
          v-if="userRole === 'HCM'"
          class="btn-add"
          @click="goToAddCandidate"
        >
          Tambah Kandidat
        </button>
      </div>

      <!-- Tabel Kandidat -->
      <table class="request-table candidates-table">
        <thead>
          <tr>
            <th>No</th>
            <th>ID</th>
            <th>Nama</th>
            <th>Email</th>
            <th>No. Telepon</th>
            <th>Domisili</th>
            <th>Posisi Dilamar</th>
            <th>Status</th>
            <th>Tanggal Daftar</th>
            <th v-if="userRole === 'HCM'">Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(candidate, index) in paginatedCandidates" :key="candidate.id">
            <td>{{ index + 1 + (currentPage - 1) * perPage }}</td>
            <td>{{ candidate.id }}</td>
            <td>{{ candidate.name }}</td>
            <td>{{ candidate.email }}</td>
            <td>{{ candidate.phone }}</td>
            <td>{{ candidate.domisili }}</td>
            <td>{{ candidate.applied_role }}</td>
            <td>
              <span :class="['status', candidate.statusClass]">{{ candidate.status }}</span>
            </td>
            <td>{{ formatDate(candidate.created_at) }}</td>
            <td v-if="userRole === 'HCM'" class="actions-cell">
              <button class="btn-edit" @click="goToEditCandidate(candidate.id)">Edit</button>
              <button class="btn-delete" @click="deleteCandidate(candidate.id)">Hapus</button>
            </td>
          </tr>
          <tr v-if="filteredCandidates.length === 0">
            <td :colspan="userRole === 'HCM' ? 10 : 9" class="text-center">
              Tidak ada kandidat.
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <div class="pagination" v-if="totalPages > 1">
        <button :disabled="currentPage === 1" @click="currentPage--">Prev</button>
        <span>Halaman {{ currentPage }} dari {{ totalPages }}</span>
        <button :disabled="currentPage === totalPages" @click="currentPage++">Next</button>
      </div>

      <!-- Alert & Confirm -->
      <div v-if="showAlert" class="alert-overlay">
        <div class="alert-box">
          <p>{{ alertMessage }}</p>
          <button @click="closeAlert">OK</button>
        </div>
      </div>
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
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "CandidatePage",
  data() {
    const user = JSON.parse(localStorage.getItem("user")) || {};
    return {
      candidates: [],
      searchQuery: "",
      token: user.token || "",
      userRole: user.role || "",
      perPage: 10,
      currentPage: 1,
      alertMessage: "",
      showAlert: false,
      confirmMessage: "",
      showConfirm: false,
      confirmCallback: null,
    };
  },
  computed: {
    filteredCandidates() {
      return this.candidates
        .filter(c => this.matchSearch(c))
        .map(c => ({ ...c, statusClass: this.getStatusClass(c.status) }));
    },
    paginatedCandidates() {
      const start = (this.currentPage - 1) * this.perPage;
      return this.filteredCandidates.slice(start, start + this.perPage);
    },
    totalPages() {
      return Math.ceil(this.filteredCandidates.length / this.perPage);
    }
  },
  watch: {
    searchQuery() {
      this.currentPage = 1;
    }
  },
  mounted() {
    this.getCandidates();
  },
  methods: {
    async getCandidates() {
      try {
        const res = await axios.get("http://localhost:5000/candidates", {
          headers: { Authorization: `Bearer ${this.token}` }
        });
        this.candidates = res.data;
      } catch (err) {
        console.error(err);
        this.showCustomAlert("Gagal mengambil data kandidat.");
      }
    },
    matchSearch(c) {
      const q = this.searchQuery.toLowerCase();
      return (
        c.name.toLowerCase().includes(q) ||
        c.email.toLowerCase().includes(q) ||
        c.phone.toLowerCase().includes(q) ||
        c.domisili.toLowerCase().includes(q) ||
        c.applied_role.toLowerCase().includes(q)
      );
    },
    getStatusClass(status) {
      return {
        'FCFS': 'new',
        'Unconfirmed': 'review',
        'Not Available': 'rejected',
        'Onboarding': 'onboard',
        'ASAP': 'interview',
        'Few Weeks': 'interview',
        '1 Month Notice': 'interview',
        '2 Month Notice': 'interview'
      }[status] || '';
    },
    goToAddCandidate() {
      this.$router.push("/add-candidate");
    },
    goToEditCandidate(id) {
      this.$router.push({ name: "EditCandidate", params: { id } });
    },
    deleteCandidate(id) {
      this.showCustomConfirm("Yakin ingin menghapus kandidat ini?", async () => {
        try {
          await axios.delete(`http://localhost:5000/candidates/${id}`, {
            headers: { Authorization: `Bearer ${this.token}` }
          });
          this.showCustomAlert("Kandidat berhasil dihapus!");
          this.getCandidates();
        } catch (err) {
          console.error(err);
          this.showCustomAlert("Gagal menghapus kandidat.");
        }
      });
    },
    formatDate(dateStr) {
      const date = new Date(dateStr);
      return date.toLocaleString("id-ID", { day: "2-digit", month: "short", year: "numeric" });
    },
    showCustomAlert(message) {
      this.alertMessage = message;
      this.showAlert = true;
    },
    closeAlert() { this.showAlert = false; },
    showCustomConfirm(message, callback) {
      this.confirmMessage = message;
      this.confirmCallback = callback;
      this.showConfirm = true;
    },
    confirmYes() { if(this.confirmCallback) this.confirmCallback(); this.showConfirm = false; },
    confirmNo() { this.showConfirm = false; },
  }
};
</script>

<style scoped>
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

/* Status Label */
.status {
  padding: 4px 10px;
  border-radius: 8px;
  color: #fff;
  font-weight: 600;
  font-size: 12px;
}
.status.new {
  background: #f1bb47;
}
.status.review {
  background: #ac1ad9;
}
.status.interview {
  background: #3f51b5;
}
.status.onboard {
  background: #43a032;
}
.status.rejected {
  background: #d33226;
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
  background: rgba(0,0,0,0.4);
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
  box-shadow: 0 4px 10px rgba(0,0,0,0.3);
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
