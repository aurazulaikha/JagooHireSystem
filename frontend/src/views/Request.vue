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

      <!-- Table Requests -->
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
              <button class="btn-delete" @click="deleteRequest(req.id)">Hapus</button>
            </td>
          </tr>
          <tr v-if="filteredRequests.length === 0">
            <td :colspan="userRole === 'HCM' ? 15 : 14" class="text-center">
              Tidak ada request.
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

      <!-- ALERT MODAL -->
      <div v-if="showAlert" class="alert-overlay">
        <div class="alert-box">
          <p>{{ alertMessage }}</p>
          <button @click="closeAlert">OK</button>
        </div>
      </div>

      <!-- CONFIRM MODAL -->
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
  name: "RequestsPage",
  data() {
    const user = JSON.parse(localStorage.getItem("user")) || {};
    return {
      requests: [],
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
    filteredRequests() {
      const q = this.searchQuery.toLowerCase();
      return this.requests.filter(
        (r) =>
          (r.role && r.role.toLowerCase().includes(q)) ||
          (r.company_name && r.company_name.toLowerCase().includes(q)) ||
          (r.location && r.location.toLowerCase().includes(q)) ||
          (r.work_method && r.work_method.toLowerCase().includes(q)) ||
          (r.level && r.level.toLowerCase().includes(q)) ||
          (r.current_stage && r.current_stage.toLowerCase().includes(q))
      );
    },
    paginatedRequests() {
      const start = (this.currentPage - 1) * this.perPage;
      return this.filteredRequests.slice(start, start + this.perPage);
    },
    totalPages() {
      return Math.ceil(this.filteredRequests.length / this.perPage);
    },
  },
  mounted() {
    this.getRequests();
  },
  methods: {
    async getRequests() {
      try {
        const res = await axios.get("http://localhost:5000/requests", {
          headers: { Authorization: `Bearer ${this.token}` },
        });
        this.requests = res.data;
      } catch (err) {
        console.error(err);
        this.showCustomAlert("Gagal mengambil data request.");
      }
    },
    goToAddRequest() {
      this.$router.push("/add-request");
    },
    goToEditRequest(id) {
      this.$router.push({ name: "EditRequest", params: { id } });
    },
    deleteRequest(id) {
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
    formatCurrency(value) {
      return new Intl.NumberFormat("id-ID", {
        style: "currency",
        currency: "IDR",
        maximumFractionDigits: 0,
      }).format(value || 0);
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
  