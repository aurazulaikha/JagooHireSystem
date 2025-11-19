<template>
  <div class="dashboard-wrapper">
    <div class="dashboard-container">
      <div class="dashboard-header">
        <h1 class="dashboard-title">Aptitude Test</h1>
        <div class="title-underline"></div>
      </div>

      <div class="form-container">
        <form @submit.prevent="testAptitude">
          <div class="form-group">
            <label>Nama Kandidat</label>
            <input v-model="form.candidate_name" readonly />
          </div>

          <div class="form-group">
            <label>Tanggal Tes</label>
            <input v-model="form.tanggal" type="date" required />
          </div>

          <div class="form-group">
            <label>Kemampuan Wajib</label>
            <input
              v-model="form.must_have_skill"
              type="must_have_skill"
              required
            />
          </div>

          <div class="form-group">
            <label>Motivasi</label>
            <select v-model="form.motivation" required>
              <option value="green_flag">Green Flag</option>
              <option value="red_flag">Red Flag</option>
            </select>
          </div>

          <div class="form-group">
            <label>Aptitude Score</label>
            <input
              v-model="form.aptitude_score"
              type="aptitude_score"
              required
            />
          </div>

          <div class="form-group">
            <label>Lanjut?</label>
            <select v-model="form.continue_next" required>
              <option value="Ya">Ya</option>
              <option value="Tidak">Tidak</option>
            </select>
          </div>

          <div class="form-group">
            <label>Notes</label>
            <textarea v-model="form.notes" rows="3"></textarea>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn-add">Simpan</button>
            <button type="button" class="btn-cancel" @click="goBack">
              Batal
            </button>
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
  name: "TestAptitudeForm",
  data() {
    const user = JSON.parse(localStorage.getItem("user")) || {};
    const selected =
      JSON.parse(localStorage.getItem("selectedCandidate")) || {};
    return {
      form: {
        request_candidate_id: selected.request_candidate_id || "",
        candidate_name: selected.candidate_name || "",
        tanggal: selected.test_date
          ? new Date(selected.test_date).toISOString().substr(0, 10)
          : "",
        must_have_skill: "",
        motivation: "",
        aptitude_score: "",
        continue_next: "",
        notes: "",
      },
      token: user.token || "",
      showPopup: false,
      popupMessage: "",
      popupType: "",
    };
  },
  methods: {
    async testAptitude() {
      try {
        await axios.post(
          "http://localhost:5000/aptitude_tests",
          {
            request_candidate_id: this.form.request_candidate_id,
            test_date: this.form.tanggal,
            must_have_skill: this.form.must_have_skill,
            motivation: this.form.motivation,
            aptitude_score: this.form.aptitude_score,
            continue_next: this.form.continue_next,
            notes: this.form.notes,
          },
          { headers: { Authorization: `Bearer ${this.token}` } }
        );

        this.showNotification("Data berhasil disimpan!", "success");
        setTimeout(() => this.$router.push("/aptitude-tests"), 1800);
      } catch (error) {
        console.error(error);
        const msg = error.response?.data?.message || "Gagal menambahkan data.";
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
      this.$router.push("/aptitude-tests");
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
