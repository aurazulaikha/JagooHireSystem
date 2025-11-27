<template>
  <div class="dashboard-wrapper">
    <div class="dashboard-container">
      <!-- Header -->
      <div class="dashboard-header">
        <h1 class="dashboard-title">Audit Logs</h1>
        <div class="title-underline"></div>
      </div>

      <!-- Actions Bar -->
      <div class="actions-bar">
        <input
          type="text"
          v-model="searchQuery"
          placeholder="Cari audit logs..."
          class="search-input"
        />
      </div>

      <!-- Tabel Audit Logs -->
      <div class="table-scroll-wrapper">
        <table class="logs-table">
          <thead>
            <tr>
              <th>No</th>
              <th>Date/Time</th>
              <th>User</th>
              <th>Category</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(log, index) in paginatedLogs" :key="log.id">
              <td>{{ (currentPage - 1) * itemsPerPage + index + 1 }}</td>
              <td>{{ formatDateTime(log.timestamp) }}</td>
              <td>{{ log.username || 'System' }}</td>
              <td>
                <span class="category-badge">{{ log.table_name }}</span>
              </td>
              <td class="action-cell">{{ log.action }}</td>
            </tr>
            <tr v-if="paginatedLogs.length === 0">
              <td colspan="5" class="text-center">
                Tidak ada data audit logs.
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
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "AuditLogs",
  data() {
    const user = JSON.parse(localStorage.getItem("user")) || {};
    return {
      logs: [],
      searchQuery: "",
      token: user.token || "",
      userRole: user.role || "",
      
      currentPage: 1,
      itemsPerPage: 10,
    };
  },
  computed: {
    filteredLogs() {
      const q = this.searchQuery.toLowerCase();
      return this.logs.filter(
        (log) =>
          (log.username || "").toLowerCase().includes(q) ||
          (log.action || "").toLowerCase().includes(q) ||
          (log.table_name || "").toLowerCase().includes(q)
      );
    },
    paginatedLogs() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      return this.filteredLogs.slice(start, start + this.itemsPerPage);
    },
    
    totalPages() {
      return Math.ceil(this.filteredLogs.length / this.itemsPerPage);
    },
  },
  watch: {
    searchQuery() {
      this.currentPage = 1;
    },
  },
  mounted() {
    this.getAuditLogs();
  },
  methods: {
    async getAuditLogs() {
      try {
        const res = await axios.get("http://localhost:5000/audit_logs", {
          headers: { Authorization: `Bearer ${this.token}` },
        });
        this.logs = res.data;
      } catch (err) {
        console.error("Gagal memuat audit logs:", err);
      }
    },
    formatDateTime(timestamp) {
      if (!timestamp) return "-";
      const date = new Date(timestamp);
      return date.toLocaleString("id-ID", {
        day: "2-digit",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
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

.table-scroll-wrapper {
  width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  border-radius: 8px;
  -webkit-overflow-scrolling: touch;
  margin-top: 10px;
}

.logs-table {
  width: 100%;
  border-collapse: collapse;
  border: 1px solid #e0d5d5;
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
}

.logs-table th,
.logs-table td {
  padding: 12px 10px;
  text-align: center;
  border-bottom: 1px solid #eee;
}

.logs-table th {
  background-color: #a26060;
  color: #fff;
  font-weight: 600;
}

.logs-table tbody tr:nth-child(even) {
  background-color: #faf6f6;
}

.logs-table tbody tr:hover {
  background-color: #f5eaea;
  transition: 0.3s;
}

.text-center {
  text-align: center;
}

.category-badge {
  display: inline-block;
  padding: 4px 10px;
  background-color: #e0d5d5;
  color: #7a3e3e;
  border-radius: 15px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.action-cell {
  text-align: left;
  max-width: 400px;
  word-wrap: break-word;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 15px;
  gap: 10px;
}

.pagination button {
  background: #a26060;
  color: white;
  border: none;
  padding: 6px 14px;
  border-radius: 6px;
  cursor: pointer;
  transition: 0.3s;
}

.pagination button:hover {
  background: #7a3e3e;
}

.pagination button:disabled {
  background: #caa7a7;
  cursor: not-allowed;
}
</style>