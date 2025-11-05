<template>
  <div class="dashboard-wrapper">
    <div class="dashboard-container">
      <!-- Header -->
      <div class="dashboard-header">
        <h1 class="dashboard-title">Tambah Request</h1>
        <div class="title-underline"></div>
      </div>

      <!-- Form Tambah Request -->
      <div class="form-container">
        <form @submit.prevent="addRequest">
          <div class="form-group">
            <label>Role Dibutuhkan</label>
            <input v-model="form.role" type="text" required />
          </div>

          <div class="form-group">
            <label>Nama Perusahaan</label>
            <input v-model="form.company_name" type="text" required />
          </div>

          <div class="form-group">
            <label>Durasi Kontrak</label>
            <input v-model="form.duration" type="text" placeholder="misal: 6 bulan" required />
          </div>

          <div class="form-group">
            <label>Jumlah Kebutuhan (Quantity)</label>
            <input v-model.number="form.quantity" type="number" min="1" required />
          </div>

          <div class="form-group">
            <label>Gaji Maksimum</label>
            <input v-model.number="form.max_salary" type="number" placeholder="misal: 8000000" />
          </div>

          <div class="form-group">
            <label>Lokasi</label>
            <input v-model="form.location" type="text" required />
          </div>

          <div class="form-group">
            <label>Metode Kerja</label>
            <select v-model="form.work_method" required>
              <option value="onsite">Onsite</option>
              <option value="hybrid">Hybrid</option>
              <option value="remote">Remote</option>
            </select>
          </div>

          <div class="form-group">
            <label>Jadwal Kerja</label>
            <input v-model="form.work_schedule" type="text" placeholder="misal: Senin - Jumat" />
          </div>

          <div class="form-group">
            <label>Perkiraan Tanggal Mulai (Est Start Date)</label>
            <input v-model="form.est_start_date" type="date" />
          </div>

          <div class="form-group">
            <label>Level Jabatan</label>
            <select v-model="form.level">
              <option value="junior">Junior</option>
              <option value="middle">Middle</option>
              <option value="senior">Senior</option>
            </select>
          </div>

          <div class="form-group">
            <label>Deskripsi Pekerjaan</label>
            <textarea v-model="form.job_description" rows="4" placeholder="Tuliskan deskripsi pekerjaan..."></textarea>
          </div>

          <div class="form-group">
            <label>Current Stage</label>
            <select v-model="form.current_stage" required>
              <option>New Request</option>
              <option>Aptitude</option>
              <option>Technical</option>
              <option>Professional</option>
              <option>Trial</option>
              <option>Onboarding</option>
              <option>Finish</option>
            </select>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn-add">Simpan</button>
            <button type="button" class="btn-cancel" @click="goBack">Batal</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Pop-up Notification -->
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
  name: "AddRequest",
  data() {
    const user = JSON.parse(localStorage.getItem("user")) || {};
    return {
      form: {
        role: "",
        company_name: "",
        duration: "",
        quantity: 1,
        max_salary: null,
        location: "",
        work_method: "onsite",
        work_schedule: "",
        est_start_date: "",
        level: "junior",
        job_description: "",
        current_stage: "New Request",
      },
      token: user.token || "",
      showPopup: false,
      popupMessage: "",
      popupType: "",
    };
  },
  methods: {
    async addRequest() {
      try {
        await axios.post(
          "http://localhost:5000/requests",
          { ...this.form },
          { headers: { Authorization: `Bearer ${this.token}` } }
        );

        this.showNotification("Request berhasil ditambahkan!", "success");

        setTimeout(() => {
          this.$router.push("/requests");
        }, 1800);
      } catch (error) {
        console.error(error);
        let msg = "Gagal menambahkan request.";
        if (error.response && error.response.data && error.response.data.message) {
          msg = error.response.data.message;
        }
        this.showNotification(msg, "error");
      }
    },
    showNotification(message, type) {
      this.popupMessage = message;
      this.popupType = type;
      this.showPopup = true;
      setTimeout(() => {
        this.showPopup = false;
      }, 2000);
    },
    goBack() {
      this.$router.push("/requests");
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
select,
textarea {
  padding: 10px 12px;
  border-radius: 8px;
  border: 1px solid #ccc;
  font-size: 14px;
  font-family: inherit;
}

textarea {
  resize: none;
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

/* Popup */
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
