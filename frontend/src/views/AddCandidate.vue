<template>
  <div class="dashboard-wrapper">
    <div class="dashboard-container">
      <div class="dashboard-header">
        <h1 class="dashboard-title">Tambah Kandidat</h1>
        <div class="title-underline"></div>
      </div>

      <div class="form-container">
        <form @submit.prevent="addCandidate">
          <div class="form-group">
            <label>Nama</label>
            <input v-model="form.name" type="text" required />
          </div>

          <div class="form-group">
            <label>Email</label>
            <input v-model="form.email" type="email" required />
          </div>

          <div class="form-group">
            <label>Nomor Telepon</label>
            <input v-model="form.no_telp" type="text" required />
          </div>

          <div class="form-group">
            <label>Domisili</label>
            <input v-model="form.domisili" type="text" required />
          </div>

          <div class="form-group">
            <label>Posisi yang Dilamar</label>
            <input v-model="form.applied_role" type="text" required />
          </div>

          <div class="form-group">
            <label>Status</label>
            <select v-model="form.status" required>
              <option value="FCFS">FCFS</option>
              <option value="Unconfirmed">Unconfirmed</option>
              <option value="Not Available">Not Available</option>
              <option value="Onboarding">Onboarding</option>
              <option value="ASAP">ASAP</option>
              <option value="Few Weeks">Few Weeks</option>
              <option value="1 Month Notice">1 Month Notice</option>
              <option value="2 Month Notice">2 Month Notice</option>
            </select>
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
  name: "AddCandidate",
  data() {
    const user = JSON.parse(localStorage.getItem("user")) || {};
    return {
      form: {
        name: "",
        email: "",
        no_telp: "",  
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
    async addCandidate() {
      try {
        await axios.post(
          "http://localhost:5000/candidates",
          { ...this.form },
          { headers: { Authorization: `Bearer ${this.token}` } }
        );

        this.showNotification("Kandidat berhasil ditambahkan!", "success");
        setTimeout(() => this.$router.push("/candidates"), 1800);
      } catch (error) {
        console.error(error);
        const msg = error.response?.data?.message || "Gagal menambahkan kandidat.";
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
      this.$router.push("/candidates");
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
