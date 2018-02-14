package embeddedwomen.flexo;

import android.support.design.widget.FloatingActionButton;
import android.support.design.widget.Snackbar;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;

import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;

import android.widget.TextView;

import org.eclipse.paho.client.mqttv3.*;

public class MainActivity extends AppCompatActivity {

    private TextView myTextView;
    MqttHelper mqttHelper;
    int[] values = new int[4];
    int exercise_tmp = 0;
    String messages = new String();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        startMqtt();
    }

    private void startMqtt(){
        mqttHelper = new MqttHelper(getApplicationContext());
        mqttHelper.setCallback(new MqttCallbackExtended() {
            @Override
            public void connectComplete(boolean b, String s) {

            }

            @Override
            public void connectionLost(Throwable throwable) {

            }

            @Override
            public void messageArrived(String topic, MqttMessage mqttMessage) throws Exception {
                messages = mqttMessage.toString();
                Log.w("Debug", messages);

                // Set up the ViewPager with the sections adapter.
                myTextView = (TextView) findViewById(R.id.flexoData);

                String arr[] = messages.split(" ");
                values[0] = Integer.parseInt(arr[1]);
                values[1] = Integer.parseInt(arr[3]);
                values[2] = Integer.parseInt(arr[5]);
                values[3] = Integer.parseInt(arr[7]);
                Log.w("Debug", "Result of split: " + String.valueOf(values[1]) + " " + String.valueOf(values[3]));
                if(values[2] != exercise_tmp) {
                    Log.w("Debug", "The text is about to be changed");
                    myTextView.setText(getString(R.string.section_1, values[0], values[1], values[3]));
                    exercise_tmp = values[2];
                }
            }

            @Override
            public void deliveryComplete(IMqttDeliveryToken iMqttDeliveryToken) {

            }
        });
    }


    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
    }
}
