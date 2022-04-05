package com.example.eve

import android.os.AsyncTask
import android.os.Bundle
import android.widget.Button
import android.widget.SeekBar
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import kotlinx.android.synthetic.main.activity_first_plant.*
import java.io.BufferedReader
import java.io.IOException
import java.io.InputStreamReader
import java.net.ConnectException
import java.net.Socket
import java.net.SocketException
import java.net.UnknownHostException


class FirstPlant : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setTheme(R.style.AppTheme)
        setContentView(R.layout.activity_first_plant)
        val bundle = intent.extras
        val socket = bundle?.getString("IP") ?: ""
        val arg = "pump/sensor/1\n"
        val soilMoistureBar = findViewById<SeekBar>(R.id.seekBar2)
        // this is the minimum reading that will happen
        // has to be done on main thread
        soilMoistureBar.min = 200
        Worker(this).execute(socket, arg)
        val arg2 = "pump/time/1\n"
        Worker(this).execute(socket, arg2)
        //prevents the disables seekbars from looking greyed out
        seekBar.setOnTouchListener { v, event -> true }
        seekBar2.setOnTouchListener { v, event -> true }



        // get the watering button
        val waterButton = findViewById<Button>( R.id.water1 )
        waterButton.setOnClickListener {
            Toast.makeText(this@FirstPlant, "You watered your plant!", Toast.LENGTH_SHORT).show()
            val arg = "pump/on/1\n"
            Worker(this).execute(socket, arg)
        }
    }

    fun makeCall(socket: String, arg: String): String {
        try {
            val client = Socket(socket, 50000)
            // connect to the raspberry pi
            client.use {
                var responseString = ""
                // write to the socket
                it.getOutputStream().write(arg.toByteArray())
//                println(arg)
                // read the response
                val bufferReader = BufferedReader(InputStreamReader(it.inputStream))
                responseString += bufferReader.readLine()

//                println("Received: $responseString")
                bufferReader.close()
                it.close()
                return responseString
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

    companion object {
        class Worker(private val firstPlant: FirstPlant) : AsyncTask<String, String, Boolean>() {        // (2)
    
             override fun doInBackground(vararg params: String?): Boolean? {
                 val in1 =  params[0] ?:  ""
                 val in2 =  params[1] ?:  ""
                 val response = firstPlant.makeCall(in1, in2)
    
                 publishProgress(response)                              // (3)
//                 Thread.sleep(100)                                         // (4)
    
                 return true
            }
    
            override fun onProgressUpdate(vararg values: String?) {
                val response = values[0] ?: ""
                println(response)
                val typeOfResponse = response.substringBefore(":")
                val contentOfResponse = response.substringAfter(":")
                if (typeOfResponse == "pumpSensor") {
                    val temp = contentOfResponse.substringBefore(",")
                    val soilTempText =
                        firstPlant.findViewById<TextView>(R.id.soilTemp)
                    // change the temp displayed
                    soilTempText.text = temp

                    val soilMoistureBar =
                        firstPlant.findViewById<SeekBar>(R.id.seekBar2)
                    val moisture = contentOfResponse.substringAfter(",")
                    // set the moisture bar
                    soilMoistureBar.setProgress(moisture.toInt(), true)
                } else if (typeOfResponse == "pumpTimer") {
                    val timerBox = firstPlant.findViewById<TextView>(R.id.timeWatered)
                    timerBox.text = contentOfResponse
                }
            }
    
            override fun onPostExecute(result: Boolean?) {
                println(result)
            }
        }
    }
}
