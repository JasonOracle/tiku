import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(localStorage.getItem('tiku_tob_token') || '');
  const username = ref<string>(localStorage.getItem('tiku_tob_username') || '');

  function setToken(newToken: string, name: string) {
    token.value = newToken;
    username.value = name;
    localStorage.setItem('tiku_tob_token', newToken);
    localStorage.setItem('tiku_tob_username', name);
  }

  function logout() {
    token.value = '';
    username.value = '';
    localStorage.removeItem('tiku_tob_token');
    localStorage.removeItem('tiku_tob_username');
  }

  return { token, username, setToken, logout };
});
