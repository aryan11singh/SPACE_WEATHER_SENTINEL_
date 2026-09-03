import DetailPage from "../../components/DetailPage";

export const metadata = {
  title: "Magnetometers",
  description: "Ground magnetic field variations tied to GIC risk."
};

export default function Page() {
  return (
    <DetailPage
      title="Magnetometers"
      meta="Ground magnetic field variations tied to GIC risk."
      cards={[
        {
          title: "Boulder Magnetometer",
          image: "https://services.swpc.noaa.gov/images/boulder-magnetometer.png",
          alt: "Boulder magnetometer"
        }
      ]}
    />
  );
}
