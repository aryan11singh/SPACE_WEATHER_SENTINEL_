import DetailPage from "../../components/DetailPage";

export const metadata = {
  title: "Solar Flares",
  description: "X-ray flux + flare imagery."
};

export default function Page() {
  return (
    <DetailPage
      title="Solar Flares"
      meta="X-ray flux + flare imagery."
      cards={[
        {
          title: "X-ray Flux",
          image: "https://services.swpc.noaa.gov/images/goes-xray-flux.gif",
          alt: "X-ray flux"
        },
        {
          title: "AIA 131",
          image: "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0131.jpg",
          alt: "AIA 131"
        }
      ]}
    />
  );
}
