<template>
  <div class="dashboard-wrapper">
    <div class="dashboard-container">
      <div class="dashboard-header">
        <h1 class="dashboard-title">Tambah User</h1>
        <div class="title-underline"></div>
      </div>

      <div class="form-container">
        <form @submit.prevent="addUser">
          <div class="form-group">
            <label>Username</label>
            <input v-model="form.username" type="text" required />
          </div>
          
          <div class="form-group">
          <label>Password</label>
        <input
          v-model="form.password"
          type="password" required
        />
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
            <label>Email</label>
            <input v-model="form.email" type="email" required />
          </div>

          <div class="form-group">
            <label>Nomor Telepon</label>
            <input v-model="form.telp" type="text" required />
          </div>

          <div class="form-actions">
            <button type="submit" class="btn-add">Simpan</button>
            <button type="button" class="btn-cancel" @click="goBack">Batal</button>
          </div>
        </form>
      </div>
    </div>

    <transition name="fade">
      <div v-if="showPopup" :class="['popup', popupType]">
        <p>{{ popupMessage }}</p>
      </div>
    </transition>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "AddUser",
  data() {
    const user = JSON.parse(localStorage.getItem("user")) || {};
    return {
      form: {
        name: "",
        email: "",
        telp: "",
        domisili: "",
        applied_role: "",
        status: "Unconfirmed",
      },
      token: user.token || "",
      showPopup: false,
      popupMessage: "",
      popupType: "",
    };
  },
  methods: {
    async addUser() {
      try {
        await axios.post(
          "http://localhost:5000/users",
          { ...this.form },
          { headers: { Authorization: `Bearer ${this.token}` } }
        );

        this.showNotification("User berhasil ditambahkan!", "success");
        setTimeout(() => this.$router.push("/users"), 1800);
      } catch (error) {
        console.error(error);
        const msg = error.response?.data?.message || "Gagal menambahkan user.";
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
/* ====== Layout dan form ====== */
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

/* ===== FORM STYLE ===== */
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
  margin-top: 20px;
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

/* ===== POPUP NOTIFICATION ===== */
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

/* Animasi muncul/hilang */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
