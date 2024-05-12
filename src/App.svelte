<script>
  import Login from "./pages/Login.svelte";
  import Main from "./pages/Main.svelte";
  import Notfound from "./pages/Notfound.svelte";
  import Signup from "./pages/Signup.svelte";
  import Write from "./pages/Write.svelte";
  import Router from "svelte-spa-router";
  import "./css/style.css";

  const routes = {
    "/": Main,
    "/login": Login,
    "/signup": Signup,
    "/write": Write,
    "*": Notfound,
  };
</script>

<Router {routes} />

<main></main>

<style></style>
