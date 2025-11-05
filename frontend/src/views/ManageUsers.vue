<template>
  <div class="dashboard-wrapper">
    <div class="dashboard-container">
      <!-- Header -->
      <div class="dashboard-header">
        <h1 class="dashboard-title">Manajemen User</h1>
        <div class="title-underline"></div>
      </div>

      <!-- Actions Bar -->
      <div class="actions-bar">
        <input
          type="text"
          v-model="searchQuery"
          placeholder="Cari user..."
          class="search-input"
        />
        <button v-if="userRole === 'HCM'" class="btn-add" @click="goToAddUser">
          Tambah User
        </button>
      </div>

      <!-- Table User -->
      <table class="request-table users-table">
        <thead>
          <tr>
            <th>No</th>
            <th>ID</th>
            <th>Username</th>
            <th>Role</th>
            <th>Email</th>
            <th>Telepon</th>
            <th>Dibuat</th>
            <th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(user, index) in paginatedUsers" :key="user.id">
            <td>{{ index + 1 + (currentPage - 1) * perPage }}</td>
            <td>{{ user.id }}</td>
            <td>{{ user.username }}</td>
            <td>{{ user.role }}</td>
            <td>{{ user.email }}</td>
            <td>{{ user.telp }}</td>
            <td>{{ formatDate(user.created_at) }}</td>
            <td v-if="userRole === 'HCM'" class="actions-cell">
              <button class="btn-edit" @click="goToEditUser(user.id)">
                Edit
              </button>
              <button class="btn-delete" @click="deleteUser(user.id)">
                Hapus
              </button>
            </td>
          </tr>
          <tr v-if="filteredUsers.length === 0">
            <td :colspan="userRole === 'HCM' ? 10 : 9" class="text-center">
              Tidak ada kandidat.
            </td>
          </tr>
        </tbody>
      </table>

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
  name: "ManageUsers",
  data() {
    const user = JSON.parse(localStorage.getItem("user")) || {};
    return {
      users: [],
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
    filteredUsers() {
      return this.users
        .filter((c) => this.matchSearch(c));
    },
    paginatedUsers() {
      const start = (this.currentPage - 1) * this.perPage;
      return this.filteredUsers.slice(start, start + this.perPage);
    },
    totalPages() {
      return Math.ceil(this.filteredUsers.length / this.perPage);
    },
  },
  watch: {
    searchQuery() {
      this.currentPage = 1;
    },
  },
  mounted() {
    this.getUsers();
  },
  methods: {
    async getUsers() {
      try {
        const res = await axios.get("http://localhost:5000/users", {
          headers: { Authorization: `Bearer ${this.token}` },
        });
        this.users = res.data;
      } catch (err) {
        console.error(err);
        this.showCustomAlert("Gagal memuat data user.");
      }
    },
    matchSearch(u) {
      const q = this.searchQuery.toLowerCase();
      return (
          u.username.toLowerCase().includes(q) ||
          (u.role && u.role.toLowerCase().includes(q)) ||
          (u.email && u.email.toLowerCase().includes(q)) ||
          (u.telp && u.telp.includes(q))
      );
    },
    goToAddUser() {
      this.$router.push("/add-user");
    },
    goToEditUser(id) {
      this.$router.push({ name: "EditUsers", params: { id } });
    },
    deleteUser(id) {
      this.showCustomConfirm("Yakin ingin menghapus user ini?", async () => {
        try {
          await axios.delete(`http://localhost:5000/users/${id}`, {
            headers: { Authorization: `Bearer ${this.token}` },
          });
          this.showCustomAlert("User berhasil dihapus!");
          this.getUsers();
        } catch (err) {
          console.error(err);
          this.showCustomAlert("Gagal menghapus user.");
        }
      });
    },
    formatDate(dateStr) {
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
