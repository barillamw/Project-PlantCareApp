package com.example.eve

import android.os.Bundle
import android.widget.Button
import android.widget.Switch
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.android.volley.Request
import com.android.volley.Response
import com.android.volley.toolbox.StringRequest
import com.android.volley.toolbox.Volley
import kotlinx.android.synthetic.main.activity_second_plant.*
import org.jetbrains.anko.doAsync
import java.io.BufferedReader
import java.io.IOException
import java.io.InputStreamReader
import java.net.ConnectException
import java.net.Socket
import java.net.SocketException
import java.net.UnknownHostException


class SecondPlant : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_second_plant)
        val bundle = intent.extras
        val socket = bundle?.getString("IP") ?: ""
        // TODO: read the sensors to get the seekbars to display current status
        //prevents the disables seekbars from looking greyed out
        seekBar.setOnTouchListener { v, event -> true }
        seekBar2.setOnTouchListener { v, event -> true }

        // get the watering button
        val waterButton = findViewById<Button>( R.id.water1 )
        waterButton.setOnClickListener {
            Toast.makeText(this@SecondPlant, "You watered your plant!", Toast.LENGTH_SHORT).show()
            val arg = "pump/on/2\n"
            val response = doAsync { makeCall( socket, arg ) }
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
