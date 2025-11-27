<template>
  <div class="dashboard-wrapper">
    <div class="dashboard-container">
      <div class="dashboard-header">
        <h1 class="dashboard-title">Technical Test</h1>
        <div class="title-underline"></div>
      </div>

      <div class="form-container">
        <form @submit.prevent="submitForm">
          <div class="form-group">
            <label>Nama Kandidat</label>
            <input v-model="form.candidate_name" readonly />
          </div>

          <div class="form-group">
            <label>Tanggal Tes</label>
            <input v-model="form.test_date" type="date" required />
          </div>

          <div class="form-group">
            <label>Domain 1 & 2 Score</label>
            <input v-model="form.domain12_score" type="number" required />
          </div>

          <div class="form-group">
            <label>Stack Eval</label>
            <select v-model="form.stack_eval" required>
              <option value="incompetent">Incompetent</option>
              <option value="developing">Developing</option>
              <option value="advance">Advance</option>
            </select>
          </div>

          <div class="form-group">
            <label>Portfolio Eval</label>
            <select v-model="form.portfolio_eval" required>
              <option value="incompetent">Incompetent</option>
              <option value="developing">Developing</option>
              <option value="advance">Advance</option>
            </select>
          </div>

          <div class="form-group">
            <label>Lanjut?</label>
            <select v-model="form.continue_next" required>
              <option value="ya">Ya</option>
              <option value="tidak">Tidak</option>
            </select>
          </div>

          <div class="form-group">
            <label>Notes</label>
            <textarea v-model="form.notes" rows="3"></textarea>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn-add">
              Simpan
            </button>
            <button type="button" class="btn-cancel" @click="goBack">
              Batal
            </button>
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
  name: "TechnicalTestForm",
  data() {
    const user = JSON.parse(localStorage.getItem("user")) || {};
    const selected = JSON.parse(localStorage.getItem("selectedCandidate")) || {};

    return {
      form: {
        rc_id: selected.rc_id || "",
        candidate_name: selected.candidate_name || "",
        test_date: this.formatDate(selected.test_date),
        domain12_score: selected.domain12_score || "",
        stack_eval: selected.stack_eval || "",
        portfolio_eval: selected.portfolio_eval || "",
        continue_next: selected.continue_next || "",
        notes: selected.notes || "",
        technical_test_id: selected.technical_test_id || null,
      },
      token: user.token,
      showPopup: false,
      popupMessage: "",
      popupType: "",
    };
  },
  methods: {
    formatDate(dateStr) {
      if (!dateStr) return "";
      return dateStr.includes("T") ? dateStr.split("T")[0] : dateStr;
    },
    async submitForm() {
      try {
        const payload = {
          rc_id: this.form.rc_id,
          test_date: this.form.test_date,
          domain12_score: parseFloat(this.form.domain12_score),
          stack_eval: this.form.stack_eval,
          portfolio_eval: this.form.portfolio_eval,
          continue_next: this.form.continue_next,
          notes: this.form.notes,
        };

        await axios.post("http://localhost:5000/technical_tests", payload, {
          headers: { Authorization: `Bearer ${this.token}` },
        });

        this.showNotification("Data berhasil disimpan!", "success");
        setTimeout(() => this.$router.push("/technical-tests"), 1800);
      } catch (error) {
        const msg = error.response?.data?.message || "Terjadi kesalahan.";
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
      this.$router.push("/technical-tests");
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
