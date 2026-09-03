import DetailPage from "../../components/DetailPage";

export const metadata = {
  title: "Coronal Mass Ejections",
  description: "Latest coronagraph imagery."
};

export default function Page() {
  return (
    <DetailPage
      title="Coronal Mass Ejections"
      meta="Latest coronagraph imagery."
      cards={[
        {
          title: "CCOR-1 (Latest)",
          image: "https://services.swpc.noaa.gov/experimental/images/ccor1/latest.png",
          alt: "CCOR-1"
        },
        {
          title: "LASCO C3",
          image: "https://sohowww.nascom.nasa.gov/data/realtime/c3/1024/latest.jpg",
          alt: "SOHO LASCO C3"
        }
      ]}
    />
  );
}
