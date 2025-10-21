import axios from "axios";

const DEFAULT_BASE_URL = "http://localhost:8000";


const httpClient = axios.create({
  baseURL: DEFAULT_BASE_URL,
});

export default httpClient;
