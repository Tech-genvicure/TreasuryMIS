import axios from "axios";


const api = axios.create({
  baseURL:
    process.env.NEXT_PUBLIC_API_URL ||
    "http://localhost:8000/api",
});


api.interceptors.request.use(
  (config) => {

    if (typeof window !== "undefined") {

      const token =
        localStorage.getItem(
          "access_token"
        );

      if (token) {

        config.headers.Authorization =
          `Bearer ${token}`;

      }

    }

    return config;
  },

  (error) => {
    return Promise.reject(error);
  }
);


api.interceptors.response.use(

  (response) => response,

  (error) => {

    if (
      error.response?.status === 401 &&
      typeof window !== "undefined"
    ) {

      localStorage.removeItem(
        "access_token"
      );

      if (
        window.location.pathname !==
        "/login"
      ) {

        window.location.href =
          "/login";

      }

    }

    return Promise.reject(error);
  }

);


export default api;