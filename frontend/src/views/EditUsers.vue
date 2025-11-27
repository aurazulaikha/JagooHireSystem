<template>
  <div class="dashboard-wrapper">
    <div class="dashboard-container">
      <div class="dashboard-header">
        <h1 class="dashboard-title">Edit User</h1>
        <div class="title-underline"></div>
      </div>

      <div class="form-container">
        <form @submit.prevent="updateUser">
          <div class="form-group">
            <label>Username</label>
            <input v-model="form.username" required />
          </div>

          <div class="form-group">
            <label>Email</label>
            <input v-model="form.email" type="email" />
          </div>

          <div class="form-group">
            <label>Nomor Telepon</label>
            <input v-model="form.telp" type="text" />
          </div>

          <div class="form-group">
            <label>Role</label>
            <select v-model="form.role" required>
              <option value="HCM">HCM</option>
              <option value="AM">AM</option>
              <option value="Director">Director</option>
            </select>
          </div>

          <div class="form-group">
            <label>Password (Opsional)</label>
            <input
              v-model="form.password"
              type="password"
              placeholder="Kosongkan jika tidak ingin mengubah"
            />
          </div>

          <div class="form-actions">
            <button type="submit" class="btn-add">Simpan Perubahan</button>
            <button type="button" class="btn-cancel" @click="goBack">Batal</button>
          </div>
        </form>
      </div>

      <!-- Pop-up Notification -->
      <transition name="fade">
        <div v-if="showPopup" :class="['popup', popupType]">
          <p>{{ popupMessage }}</p>
        </div>
      </transition>
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
      token: user.token,
      showPopup: false,
      popupMessage: "",
      popupType: "",
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
          this.showNotification("User tidak ditemukan.", "error");
        }
      } catch (err) {
        this.showNotification("Gagal memuat data user.", "error");
      }
    },
    async updateUser() {
      try {
        await axios.put(
          `http://localhost:5000/users/${this.form.id}`,
          this.form,
          { headers: { Authorization: `Bearer ${this.token}` } }
        );
        this.showNotification("User berhasil diperbarui!", "success");
        setTimeout(() => this.goBack(), 1800);
      } catch (err) {
        const msg = err.response?.data?.message || "Gagal memperbarui user.";
        this.showNotification(msg, "error");
      }
    },
    showNotification(message, type) {
      this.popupMessage = message;
      this.popupType = type;
      this.showPopup = true;
      setTimeout(() => (this.showPopup = false), 2000);
    },
    goBack() {
      this.$router.push("/users");
    },
  },
};
</script>

<style scoped>
.dashboard-wrapper {
  background: linear-gradient(180deg, #f9f3f3, #fff);
  min-height: 100vh;
  display: flex;
  justify-content: flex-start;
  align-items: flex-start;
  padding: 80px 60px;
  box-sizing: border-box;
  position: relative;
}
.dashboard-container {
  width: 100%;
  max-width: 800px;
  color: #333;
  font-family: "Poppins", sans-serif;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 25px;
}
.dashboard-header {
  text-align: left;
  width: 100%;
}
.dashboard-title {
  font-size: 32px;
  font-weight: 700;
  color: #7a3e3e;
  margin-bottom: 10px;
  text-align: left;
}
.title-underline {
  width: 80px;
  height: 4px;
  background: #a26060;
  border-radius: 5px;
  margin-bottom: 25px;
}

.form-container {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 25px;
  width: 100%;
  max-width: 600px;
}
.form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 15px;
}

label {
  font-weight: 600;
  margin-bottom: 6px;
  color: #7a3e3e;
}
input,
select {
  padding: 10px 12px;
  border-radius: 8px;
  border: 1px solid #ccc;
  font-size: 14px;
  font-family: inherit;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 15px;
}
.btn-add {
  background: #a26060;
  color: #fff;
  padding: 10px 16px;
  border-radius: 8px;
  border: none;
  font-weight: 600;
  cursor: pointer;
  transition: 0.3s;
}
.btn-add:hover {
  background: #7a3e3e;
}
.btn-cancel {
  background: #ccc;
  color: #333;
  padding: 10px 16px;
  border-radius: 8px;
  border: none;
  font-weight: 600;
  cursor: pointer;
  transition: 0.3s;
}
.btn-cancel:hover {
  background: #999;
}

.popup {
  position: fixed;
  top: 30px;
  left: 50%;
  transform: translateX(-50%);
  padding: 16px 24px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 15px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.15);
  color: #fff;
  z-index: 1000;
  opacity: 0.95;
}
.popup.success {
  background-color: #4caf50;
}
.popup.error {
  background-color: #f44336;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
