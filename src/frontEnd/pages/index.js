// frontend/pages/index.js
export default function Index() {
  return null;
}

// redireciona para o HTML estático em /public/homePage.html
export async function getServerSideProps() {
  return {
    redirect: {
      destination: '/homePage.html',
      permanent: false,
    },
  };
}