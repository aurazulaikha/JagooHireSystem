<template>
  <div class="edit-user-wrapper">
    <div class="edit-user-container">
      <h1 class="page-title">Edit Pengguna</h1>
      <div class="title-underline"></div>

      <form @submit.prevent="updateUser">
        <label>Username</label>
        <input v-model="form.username" required />

        <label>Email</label>
        <input v-model="form.email" type="email" required />

        <label>No. Telepon</label>
        <input v-model="form.telp" placeholder="Masukkan nomor telepon" />

        <label>Role</label>
        <select v-model="form.role" required>
          <option value="">Pilih Role</option>
          <option value="HCM">HCM</option>
          <option value="AM">AM</option>
          <option value="Director">Director</option>
        </select>

        <label>Password (Opsional)</label>
        <input
          v-model="form.password"
          type="password"
          placeholder="Isi jika ingin mengganti password"
        />

        <div class="form-actions">
          <button type="submit">Simpan Perubahan</button>
          <button type="button" @click="goBack">Batal</button>
        </div>
      </form>

      <!-- ALERT -->
      <div v-if="showAlert" :class="['alert-box', alertType]">
        <p>{{ alertMessage }}</p>
        <button @click="closeAlert">OK</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "EditUsers",
  data() {
    const user = JSON.parse(localStorage.getItem("user")) || {};
    return {
      form: {
        id: null,
        username: "",
        email: "",
        telp: "",
        role: "",
        password: "",
      },
      token: user.token || "",
      showAlert: false,
      alertMessage: "",
      alertType: "",
      alertCallback: null,
    };
  },
  mounted() {
    this.loadUser();
  },
  methods: {
    async loadUser() {
      const userId = this.$route.params.id;
      try {
        const res = await axios.get("http://localhost:5000/users", {
          headers: { Authorization: `Bearer ${this.token}` },
        });
        const user = res.data.find((u) => u.id == userId);
        if (user) {
          this.form = { ...user, password: "" };
        } else {
          this.showCustomAlert("User tidak ditemukan.", "error");
        }
      } catch (err) {
        console.error(err);
        this.showCustomAlert("Gagal memuat data user.", "error");
      }
    },
    async updateUser() {
      try {
        await axios.put(
          `http://localhost:5000/users/${this.form.id}`,
          { ...this.form },
          { headers: { Authorization: `Bearer ${this.token}` } }
        );
        this.showCustomAlert("User berhasil diperbarui!", "success", () => {
          this.goBack();
        });
      } catch (err) {
        console.error(err);
        const msg = err.response?.data?.message || "Gagal memperbarui user.";
        this.showCustomAlert(msg, "error");
      }
    },
    goBack() {
      this.$router.push("/users");
    },
    showCustomAlert(message, type = "success", callback = null) {
      this.alertMessage = message;
      this.alertType = type;
      this.showAlert = true;
      this.alertCallback = callback;
    },
    closeAlert() {
      this.showAlert = false;
      if (this.alertCallback) this.alertCallback();
    },
  },
};
</script>

<style scoped>
.edit-user-wrapper {
  display: flex;
  justify-content: flex-start;
  padding: 100px 0 0 50px;
  min-height: 100vh;
  background: linear-gradient(180deg, #f9f3f3, #fff);
}

.edit-user-container {
  width: 400px;
  background: #fff;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  gap: 15px;
}

/* Header */
.page-title {
  font-size: 28px;
  color: #7a3e3e;
  font-weight: 700;
}

.title-underline {
  width: 80px;
  height: 4px;
  background: #a26060;
  border-radius: 5px;
  margin-bottom: 15px;
}

/* Form */
form label {
  display: block;
  margin-top: 10px;
  font-weight: 500;
}

form input,
form select {
  width: 100%;
  padding: 8px;
  border-radius: 6px;
  border: 1px solid #ccc;
  margin-top: 5px;
}

/* Form actions */
.form-actions {
  margin-top: 15px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.form-actions button {
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.form-actions button[type="submit"] {
  background: #43a032;
  color: white;
}

.form-actions button[type="button"] {
  background: #ccc;
  color: #333;
}

/* Alert */
.alert-box {
  margin-top: 15px;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
  font-weight: 500;
}

.alert-box.success {
  background: #d1e7dd;
  color: #0f5132;
}

.alert-box.error {
  background: #f8d7da;
  color: #842029;
}

.alert-box button {
  margin-top: 10px;
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  background: #333;
  color: #fff;
}
</style>
