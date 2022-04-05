package com.example.eve


import android.app.AlertDialog.THEME_DEVICE_DEFAULT_DARK
import android.app.AlertDialog.THEME_DEVICE_DEFAULT_LIGHT
import android.content.DialogInterface
import android.content.Intent
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.ImageView
import android.widget.Switch
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import com.skydoves.colorpickerview.ColorEnvelope
import com.skydoves.colorpickerview.ColorPickerDialog
import com.skydoves.colorpickerview.listeners.ColorEnvelopeListener
import com.skydoves.colorpickerview.listeners.ColorPickerViewListener
import org.jetbrains.anko.doAsync
import java.io.BufferedReader
import java.io.IOException
import java.io.InputStreamReader
import java.net.ConnectException
import java.net.Socket
import java.net.SocketException
import java.net.UnknownHostException


class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        // do this before the onCreate to make sure we have the right theme
        setTheme(R.style.AppTheme)
        // start normally now
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        val socket = "192.168.50.47"


        // Open first plant on click
        val first = findViewById<ImageView>(R.id.plant1)
        // set on-click listener
        first.setOnClickListener {
            // open plant's page
            val intent = Intent(this, FirstPlant::class.java)
            intent.putExtra("IP", socket)

            //Start new Activity
            startActivity(intent)
        }

        // Open second plant on click
        val second = findViewById<ImageView>(R.id.plant2)
        // set on-click listener
        second.setOnClickListener {
            // open second plant's page
            val intent = Intent(this, SecondPlant::class.java)
            intent.putExtra("IP", socket)
            //Start new Activity
            startActivity(intent)
        }

        // Open third plant on click
        val third = findViewById<ImageView>(R.id.plant3)
        // set on-click listener
        third.setOnClickListener {
            // open third plant's page
            val intent = Intent(this, ThirdPlant::class.java)
            intent.putExtra("IP", socket)
            //Start new Activity
            startActivity(intent)
        }

        // Open fourth plant on click
        val fourth = findViewById<ImageView>(R.id.plant4)
        // set on-click listener
        fourth.setOnClickListener {
            // open fourth plant's page
            val intent = Intent(this, FourthPlant::class.java)
            intent.putExtra("IP", socket)
            //Start new Activity
            startActivity(intent)
        }

        // get the switch
        val lightSwitch = findViewById<Switch>( R.id.light1 )
        // set onClick listener
        lightSwitch.setOnCheckedChangeListener { _, isChecked ->
            val arg = if (isChecked) {
                "light/on\n"
            } else {
                "light/off\n"
            }
            val response = doAsync { makeCall(socket, arg) }
        }

        val colorButton = findViewById<Button>(R.id.colorButton)
        colorButton.setOnClickListener{
            ColorPickerDialog.Builder (this, R.color.colorPrimary)
            .setTitle("Choose EVE's light color")
            .setPreferenceName("EVE's light color")
            .setPositiveButton(getString(R.string.confirm),
                ColorEnvelopeListener() { colorEnvelope: ColorEnvelope, b: Boolean ->
                    println(colorEnvelope.argb[0])
                    println(colorEnvelope.argb[1])
                    println(colorEnvelope.argb[2])
                    println(colorEnvelope.argb[3])
                    println(colorEnvelope.argb.size)
                    val arg = "light/on/3/(${colorEnvelope.argb[1]},${colorEnvelope.argb[2]},${colorEnvelope.argb[3]})\n"
                    val response = doAsync { makeCall(socket, arg) }
                })
                .setNegativeButton(getString(R.string.cancel)) { dialogInterface: DialogInterface, i: Int ->
                    dialogInterface.dismiss()
                }
                .attachAlphaSlideBar(false) // default is true. If false, do not show the AlphaSlideBar.
                .attachBrightnessSlideBar(false)  // default is true. If false, do not show the BrightnessSlideBar.
                .show();
            }
        }


    fun makeCall(socket: String, arg: String): String {
        try {
            val client = Socket(socket, 50000)
            // connect to the raspberry pi
            client.use {
                var responseString: String = ""
                // write to the socket
                it.getOutputStream().write(arg.toByteArray())
//                println(arg)
                // read the response
                val bufferReader = BufferedReader(InputStreamReader(it.inputStream))
                responseString += bufferReader.readLine()

//                println("Received: $responseString")
                bufferReader.close()
                it.close()
                return responseString!!
            }
        } catch (he: UnknownHostException) {
            return "An exception occurred:\n ${he.printStackTrace()}"
        } catch (ioe: IOException) {
            return "An exception occurred:\n ${ioe.printStackTrace()}"
        } catch (ce: ConnectException) {
            return "An exception occurred:\n ${ce.printStackTrace()}"
        } catch (se: SocketException) {
            return "An exception occurred:\n ${se.printStackTrace()}"
        }
    }
}
